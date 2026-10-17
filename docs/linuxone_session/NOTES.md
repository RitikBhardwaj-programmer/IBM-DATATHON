# LinuxONE Setup & Tech Prep Session (16 Oct 2026): notes

Source: https://www.youtube.com/live/HrNNkVyFots (55 min, Shooting Stars Foundation).
Speakers: Dr. Alex Osadchyy (IBM Z & LinuxONE Ecosystem Lead Solution Architect), Bruce Gilkes (IBM Z & LinuxONE Community Clouds Program Manager).

How this was made: the video has no YouTube captions; Zoom burned the captions into the picture. `transcript_ocr.txt` = Windows OCR of the caption strip every 2 s, de-duplicated (noisy: read it for meaning, not for exact words). `slides/` = frames from the 720p video, named `<mm-ss>_<topic>.png`. Facts below come from the slides unless marked (speech).

## Must-know for setup

| Item | Value | Where |
|---|---|---|
| Event code | **`SSF2026`** (put it in the project description at registration) | slide 53:50 |
| Without the event code | no `AI_LAB` flavor; email linux1@us.ibm.com or ask on Discord to delete the registration, then register again with the code (speech) | 13:08, 17:20 |
| Registration | https://linuxone.cloud.marist.edu/#/register?flag=VM | 09:43 |
| Dashboard | https://linuxone.cloud.marist.edu/#/login | 09:43 |
| Instructions | https://ibm.biz/BdPcL8 | 53:50 |
| FAQs | https://community.ibm.com/zsystems/datathon/ | 09:43 |
| Lab guide (Jupyter) | https://github.com/linuxone-community-cloud/jupyter-lab-ml | 09:43 |
| Server guide | https://github.com/linuxone-community-cloud/technical-resources/blob/master/faststart/deploy-virtual-server.md | 09:43 |
| PuTTY guide | .../technical-resources/blob/master/faststart/PUTTY_Set_up.pdf | 09:43 |
| VM | 3 vCPU, 8 GB RAM, 50 GB disk; 30-day trial; full root via SSH; user `linux1` | 08:40, 16:40 |
| Image | choose the **`-datathon`** images: Ubuntu 24.04 datathon or RHEL 9.8 datathon (speech) | 16:30 |
| Flavor | `AI_LAB` (3 cores, 8192 MB, 50 GB) | 16:40 |
| Activation | click the link in the first email, or the login never works (speech) | 13:58 |
| Server creation time | 15-20 min when thousands are created at once; status `shutdown` is OK, press Start (speech) | 18:16 |
| One server per **team** | not one per user (speech) | 26:04 |
| Hardware | IBM z17 / LinuxONE 5 at Marist University, NY; machine type 9175; hypervisor z/VM; `lscpu \| grep -i nnpa` shows the Telum II AI accelerator (NNPA) is enabled | 08:17, 23:36 |
| Reused IP | if SSH complains about host key, delete the old line in `~/.ssh/known_hosts` (speech) | 21:46 |

## Jupyter lab container (slide 37:30)

```bash
docker pull registry.linuxone.cloud.marist.edu/l1cc/jupyterlab-image-s390x:latest
mkdir shared && chmod a+w shared
docker run --network host --name notebook -v /home/linux1/shared:/home/ibm-user/shared \
  -d registry.linuxone.cloud.marist.edu/l1cc/jupyterlab-image-s390x:latest
sudo iptables -I INPUT -p tcp --dport 38888 -j ACCEPT
```
You may need `--security-opt seccomp=unconfined`. URL `http://<public IP>:38888`; the default token is `Your_Token1`. **Change it** (append `jupyter notebook --ip=0.0.0.0 --port=38888 --ServerApp.port=38888 --ServerApp.token='...' --ServerApp.allow_origin='*'` to the run command): the VM has a public IP. The image has 100+ packages pre-installed (PyTorch, TensorFlow, scikit-learn, XGBoost, llama.cpp) (speech 04:06).

## Reference labs (do not submit them unchanged)
1. Credit-card fraud, 2-layer LSTM on 24 M transactions, exported to ONNX, NNPA-accelerated.
2. Hybrid loan approval: XGBoost risk score + RAG over bank policy + IBM Granite LLM (new this year).
3. Churn/profitability: scikit-learn + PyTorch logistic regression.
4. MNIST CNN in TensorFlow/Keras, ONNX; demo: median inference 3.6 ms per image on 3 vCPU + accelerator.

## Six-step workflow (slide 05:34)
Register on L1CC → deploy Jupyter stack → run reference labs → build solution (one of 3 themes; **"Implement all application and modeling code from scratch during the hackathon period"**) → meet the criteria → present and submit (screenshots of Jupyter on LinuxONE, presentation video within the time limit, official portal).

## Themes (slide 50:19)
1. Real-Time AI for Critical Decisions.
2. **AI Secured: Innovation Without Exposure**: "Build privacy-preserving AI that learns from sensitive datasets while protecting identity, trust, and regulatory compliance." Core principle: build security and privacy into the application core.
3. Wildcard: Beyond the Obvious.

## Scoring: 4 x 10 = 40 (slide 52:30)
- **Technical Design** (most weight, speech 52:06): video/screenshots of workloads running live on L1CC; at least 2 AI open-source frameworks (e.g. PyTorch + XGBoost); containerized deployment with Docker/Podman; highlight platform security or Telum AI acceleration.
- **Novelty & Originality:** write 100% of solution code from scratch during the hackathon; don't submit reference notebooks unchanged; combine hybrid AI techniques; pair structured predictive models with LLM reasoning (Granite).
- **Pitch & Delivery:** strictly keep to the video time limit; problem, target persona, value proposition; live interactive demo recorded on LinuxONE; team member roles and contributions.
- **Community Value:** a specific, quantified beneficiary population; tie explicitly to one theme; frame as "AI for Good"; ethical AI and transparent decision reasoning.

Questions go to the Discord channels with IBM SMEs; Adam presents the themes in depth at the kick-off (speech 51:14, 54:32).
