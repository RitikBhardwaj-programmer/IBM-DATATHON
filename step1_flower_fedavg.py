"""Step 1: plain FedAvg with Flower simulation + PyTorch, on deliberately non-IID data.

Story: 3 simulated hospitals each hold a private slice of the breast-cancer dataset.
Raw rows never leave a client; only model parameters travel to the server.

Run:  .venv\\Scripts\\python.exe step1_flower_fedavg.py
"""
import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from flwr.client import ClientApp, NumPyClient
from flwr.common import Context, ndarrays_to_parameters
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg
from flwr.simulation import run_simulation

SEED = 0
NUM_CLIENTS = 3
NUM_ROUNDS = 10
LOCAL_EPOCHS = 1
DIRICHLET_ALPHA = 0.5  # smaller -> more non-IID (hospitals see very different label mixes)

torch.manual_seed(SEED)
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- data
X, y = load_breast_cancer(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=SEED
)
scaler = StandardScaler().fit(X_train)  # fit on train only: no test leakage
X_train = scaler.transform(X_train).astype("float32")
X_test = scaler.transform(X_test).astype("float32")
y_train = y_train.astype("float32")
y_test = y_test.astype("float32")


def dirichlet_partition(labels, num_clients, alpha):
    """Split indices so each client gets a different class mix (label-skew non-IID)."""
    shards = [[] for _ in range(num_clients)]
    for cls in np.unique(labels):
        idx = np.where(labels == cls)[0]
        rng.shuffle(idx)
        props = rng.dirichlet([alpha] * num_clients)
        cuts = (np.cumsum(props) * len(idx)).astype(int)[:-1]
        for shard, part in zip(shards, np.split(idx, cuts)):
            shard.extend(part.tolist())
    return [np.array(s) for s in shards]


partitions = dirichlet_partition(y_train, NUM_CLIENTS, DIRICHLET_ALPHA)
for i, p in enumerate(partitions):
    print(f"hospital {i}: {len(p):3d} patients, {int(y_train[p].sum()):3d} benign / {int((1 - y_train[p]).sum()):3d} malignant")


# ---------------------------------------------------------------- model
class Net(nn.Module):
    def __init__(self, n_features=X.shape[1]):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_features, 16), nn.ReLU(), nn.Linear(16, 1))

    def forward(self, x):
        return self.net(x).squeeze(1)  # logits


def get_parameters(model):
    return [v.cpu().numpy() for v in model.state_dict().values()]


def set_parameters(model, params):
    keys = model.state_dict().keys()
    model.load_state_dict({k: torch.tensor(v) for k, v in zip(keys, params)}, strict=True)


def train(model, loader, epochs):
    opt = torch.optim.SGD(model.parameters(), lr=0.05)
    loss_fn = nn.BCEWithLogitsLoss()
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()


@torch.no_grad()
def test(model, X_, y_):
    model.eval()
    logits = model(torch.from_numpy(X_))
    loss = nn.BCEWithLogitsLoss()(logits, torch.from_numpy(y_)).item()
    pred = (logits > 0).int().numpy()
    return loss, float((pred == y_).mean()), float(f1_score(y_, pred))


# ---------------------------------------------------------------- Flower client
class HospitalClient(NumPyClient):
    def __init__(self, idx):
        self.model = Net()
        ds = TensorDataset(torch.from_numpy(X_train[idx]), torch.from_numpy(y_train[idx]))
        self.loader = DataLoader(ds, batch_size=16, shuffle=True)
        self.n = len(idx)

    def get_parameters(self, config):
        return get_parameters(self.model)

    def fit(self, parameters, config):  # LEARN
        set_parameters(self.model, parameters)
        train(self.model, self.loader, LOCAL_EPOCHS)
        return get_parameters(self.model), self.n, {}

    def evaluate(self, parameters, config):  # MEASURE (on this hospital's local data)
        set_parameters(self.model, parameters)
        idx = partitions[self._pid]
        loss, acc, _ = test(self.model, X_train[idx], y_train[idx])
        return loss, self.n, {"accuracy": acc}


def client_fn(context: Context):
    pid = int(context.node_config["partition-id"])
    client = HospitalClient(partitions[pid])
    client._pid = pid
    return client.to_client()


# ---------------------------------------------------------------- Flower server
history = []


def global_eval(server_round, parameters, config):
    """Server-side evaluation on a held-out global test set (for our own reporting)."""
    model = Net()
    set_parameters(model, parameters)
    loss, acc, f1 = test(model, X_test, y_test)
    history.append((server_round, loss, acc, f1))
    print(f"round {server_round:2d} | global test loss {loss:.4f} | acc {acc:.3f} | F1 {f1:.3f}")
    return loss, {"accuracy": acc, "f1": f1}


def weighted_avg(metrics):
    total = sum(n for n, _ in metrics)
    return {"accuracy": sum(n * m["accuracy"] for n, m in metrics) / total}


def server_fn(context: Context):
    strategy = FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=NUM_CLIENTS,
        min_evaluate_clients=NUM_CLIENTS,
        min_available_clients=NUM_CLIENTS,
        initial_parameters=ndarrays_to_parameters(get_parameters(Net())),
        evaluate_fn=global_eval,
        evaluate_metrics_aggregation_fn=weighted_avg,
    )
    return ServerAppComponents(strategy=strategy, config=ServerConfig(num_rounds=NUM_ROUNDS))


if __name__ == "__main__":
    # Baseline: one centralized model on all pooled training data (the number to compare against).
    central = Net()
    pooled = DataLoader(TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train)), batch_size=16, shuffle=True)
    train(central, pooled, epochs=NUM_ROUNDS * LOCAL_EPOCHS)
    _, c_acc, c_f1 = test(central, X_test, y_test)
    print(f"\ncentralized baseline | acc {c_acc:.3f} | F1 {c_f1:.3f}\n")

    run_simulation(
        server_app=ServerApp(server_fn=server_fn),
        client_app=ClientApp(client_fn=client_fn),
        num_supernodes=NUM_CLIENTS,
    )
    r, _, acc, f1 = history[-1]
    print(f"\nFedAvg after {r} rounds | acc {acc:.3f} | F1 {f1:.3f}  (centralized: acc {c_acc:.3f} | F1 {c_f1:.3f})")
