"""Create the TLS certificates for the step 6 deployment: a self-signed CA and one SuperLink server certificate.

    .venv\\Scripts\\python.exe deploy/gen_certs.py            (writes deploy/certs/; keeps existing files)
    .venv\\Scripts\\python.exe deploy/gen_certs.py --force    (new CA and server key)
    .venv\\Scripts\\python.exe deploy/gen_certs.py --out DIR  (another folder; run_step6_local.py uses its own work dir)

Files: ca.crt (public: SuperNodes, the flwr CLI and the dashboard get only this), ca.key (signs; in Docker only the `certs` service
sees it), server.pem + server.key (SuperLink only). Keys are written owner-only (0600).
deploy/certs/ is gitignored: a private key must never be committed. Uses `cryptography` (already a Flower dependency), so it runs the
same on Windows, on the laptop and inside the image; no openssl needed.

The server certificate is valid for every name a client uses to reach the SuperLink:
  superlink    Docker service name (SuperNodes and the dashboard container)
  localhost, 127.0.0.1, ::1   the native run, and Flower's own flower-superexec child, which connects to the Runtime API at
                              127.0.0.1 when the SuperLink binds 0.0.0.0 (flwr.supercore.address.resolve_bind_address)
A name missing here does not fail loudly: the client retries the handshake until it times out.
"""
import argparse
import datetime as dt
import ipaddress
import os
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

DNS_NAMES = ["superlink", "localhost"]
IP_NAMES = ["127.0.0.1", "::1"]
DAYS = 365
FILES = ("ca.crt", "ca.key", "server.pem", "server.key")


def _key():
    return ec.generate_private_key(ec.SECP256R1())


def _write_key(path, key):
    path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    os.chmod(path, 0o600)  # owner only (on Windows this only clears write bits; the file stays in the user's own folder)


def _still_good(out):
    """True if the existing server certificate has today's SAN list and is valid for at least one more day."""
    try:
        cert = x509.load_pem_x509_certificate((out / "server.pem").read_bytes())
        sans = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    except (OSError, ValueError, x509.ExtensionNotFound):
        return False
    names = set(sans.get_values_for_type(x509.DNSName)) | {str(a) for a in sans.get_values_for_type(x509.IPAddress)}
    left = cert.not_valid_after_utc - dt.datetime.now(dt.timezone.utc)
    return names == set(DNS_NAMES + IP_NAMES) and left > dt.timedelta(days=1)


def _write_cert(path, cert):
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def generate(out, force=False):
    """Write the four files into `out` (created if needed). Returns `out`. Existing files are kept unless force=True or the server
    certificate is expiring (< 1 day left) or has another SAN list (an expired or misnamed cert would make clients retry forever)."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if not force and all((out / f).is_file() for f in FILES) and _still_good(out):
        return out
    now = dt.datetime.now(dt.timezone.utc)
    start, end = now - dt.timedelta(minutes=5), now + dt.timedelta(days=DAYS)  # small back-date: container clocks drift

    ca_key = _key()
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Zero Exposure demo CA")])
    ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name).public_key(ca_key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(start).not_valid_after(end)
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(digital_signature=False, content_commitment=False, key_encipherment=False, data_encipherment=False,
                                       key_agreement=False, key_cert_sign=True, crl_sign=True, encipher_only=False, decipher_only=False),
                         critical=True)
          .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False)
          .sign(ca_key, hashes.SHA256()))

    srv_key = _key()
    sans = [x509.DNSName(n) for n in DNS_NAMES] + [x509.IPAddress(ipaddress.ip_address(a)) for a in IP_NAMES]
    srv = (x509.CertificateBuilder()
           .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "superlink")])).issuer_name(ca_name)
           .public_key(srv_key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(start).not_valid_after(end)
           .add_extension(x509.SubjectAlternativeName(sans), critical=False)
           .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
           .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
           .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
           .sign(ca_key, hashes.SHA256()))

    _write_key(out / "ca.key", ca_key)
    _write_cert(out / "ca.crt", ca)
    _write_key(out / "server.key", srv_key)
    _write_cert(out / "server.pem", srv)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=Path(__file__).parent / "certs")
    ap.add_argument("--force", action="store_true", help="replace existing files (new CA: every component must get the new ca.crt)")
    a = ap.parse_args()
    d = generate(a.out, a.force)
    print(f"certificates in {d}: {', '.join(FILES)} (server names: {', '.join(DNS_NAMES + IP_NAMES)}; valid {DAYS} days)")
