# perf-agent Dependencies

Required components (install on self-hosted runners or ensure available in GitHub-hosted environment):

- Docker (for running JMeter image `justb4/jmeter:5.5`) OR Apache JMeter installed and on `PATH`.
- Python 3.x
- Python packages: listed in root `requirements.txt` (`lxml`, `jinja2`).
- (Optional) `xmlstarlet` if you prefer XML CLI modifications.

Installation (Ubuntu example):

```bash
sudo apt update
sudo apt install -y docker.io python3 python3-pip
python3 -m pip install -r requirements.txt
```

Windows (PowerShell) guidance:

1. Install Docker Desktop and enable WSL2.
2. Install Python 3 and run `pip install -r requirements.txt`.
