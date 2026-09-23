# Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel

This guide provides a complete, step-by-step procedure for deploying FPOLink TN to production at **zero monthly hosting cost** using **Oracle Cloud Infrastructure (OCI) Always Free Tier** and **Cloudflare Zero Trust Tunnels**.

---

## 1. Architecture & Cost Model

```text
[ Meta WhatsApp Webhook / Farmers / Staff ]
                     │
                     ▼ (HTTPS: 443)
            [ Cloudflare Edge ]
                     │
                     │ (Encrypted Outbound Tunnel)
                     ▼
    [ Oracle Cloud Always Free VM (Ubuntu) ]
      └── [ cloudflared connector container ]
            └── [ Docker Network: backend:8000, frontend:3000 ]
```

- **Compute**: Oracle Cloud Always Free Tier (Up to 4 OCPU / 24 GB RAM on Ampere A1 ARM64, or 1 OCPU / 1 GB RAM on AMD Micro) — **₹0.00/month**.
- **Ingress & SSL**: Cloudflare Zero Trust Tunnel (50 free users, DDoS protection, automatic managed SSL certificates) — **₹0.00/month**.
- **Database**: Self-hosted PostgreSQL 16 container with local persistent volume — **₹0.00/month**.
- **Inbound Ports Open**: **Zero**. No public IP required, no firewall ports opened to the public internet.

---

## 2. Oracle Cloud VM Provisioning

### Step 1: Create an Oracle Cloud Account
1. Sign up at [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/).
2. Select your home region (e.g. `ap-mumbai-1` or `ap-hyderabad-1` for lowest latency to Tamil Nadu).

### Step 2: Launch Compute Instance
1. In the OCI Console, navigate to **Compute** > **Instances** > **Create Instance**.
2. **Name**: `fpolink-production-vm`.
3. **Image**: `Ubuntu 22.04 LTS` or `Ubuntu 24.04 LTS`.
4. **Shape**:
   - Recommended: **Ampere ARM (VM.Standard.A1.Flex)** with 2 OCPU, 12 GB RAM (Always Free Eligible).
   - Alternatively: **AMD (VM.Standard.E2.1.Micro)** with 1 OCPU, 1 GB RAM.
5. **Networking**: Select your default VCN and public subnet (or private subnet with NAT gateway).
6. **SSH Keys**: Download and save your private SSH key (`id_rsa_oci`).
7. Click **Create** and wait for the instance state to change to `RUNNING`.

---

## 3. Host Initialization & Docker Installation

### Step 1: Connect via SSH
```bash
ssh -i /path/to/id_rsa_oci ubuntu@<YOUR_VM_IP>
```

### Step 2: Update System & Install Docker
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg git

# Install Docker Engine & Docker Compose plugin
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow ubuntu user to run Docker without sudo
sudo usermod -aG docker ubuntu
newgrp docker
```

---

## 4. Cloudflare Zero Trust Tunnel Setup

### Step 1: Create Tunnel in Cloudflare Dashboard
1. Log in to [Cloudflare One Dashboard](https://one.dash.cloudflare.com/).
2. Go to **Networks** > **Tunnels** > **Create a tunnel**.
3. Select **Cloudflared** connector and name it `fpolink-production`.
4. Under **Install connector**, select **Docker** and copy the tunnel token (e.g. `eyJhIjoi...`).

### Step 2: Route Hostnames
Under the **Public Hostnames** tab of your tunnel:

1. **API & Webhooks**:
   - Subdomain: `api`
   - Domain: `yourfpo.org`
   - Service Type: `HTTP`
   - URL: `backend:8000`

2. **Staff Dashboard (Optional)**:
   - Subdomain: `app` (or `dashboard`)
   - Domain: `yourfpo.org`
   - Service Type: `HTTP`
   - URL: `frontend:3000`

Save the tunnel configuration.

---

## 5. Clone and Configure FPOLink

### Step 1: Clone Repository
```bash
cd /opt
sudo git clone https://github.com/4LPH7/FPOLink.git
sudo chown -R ubuntu:ubuntu /opt/FPOLink
cd /opt/FPOLink
```

### Step 2: Configure Production `.env`
```bash
cp .env.example .env
nano .env
```

Set the following production values:
```dotenv
# Environment & Security
ENVIRONMENT=production
SECRET_KEY=<generate_random_32_char_secret_key>

# Database Credentials
POSTGRES_USER=fpolink_prod
POSTGRES_PASSWORD=<generate_strong_db_password>
POSTGRES_DB=fpolink_prod
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://fpolink_prod:<generate_strong_db_password>@postgres:5432/fpolink_prod

# WhatsApp Cloud API
WHATSAPP_ENABLED=true
WHATSAPP_VERIFY_TOKEN=<secure_random_string_for_webhook_verify>
WHATSAPP_APP_SECRET=<from_meta_app_dashboard>
WHATSAPP_ACCESS_TOKEN=<from_meta_system_user_permanent_token>
WHATSAPP_PHONE_NUMBER_ID=<from_meta_whatsapp_manager>
WHATSAPP_BOT_PHONE=919876543210

# Cloudflare Tunnel Token
CLOUDFLARE_TUNNEL_TOKEN=<token_copied_from_cloudflare_dashboard>

# Frontend Public API URL
NEXT_PUBLIC_API_URL=https://api.yourfpo.org

# Optional Sentry Error Monitoring
SENTRY_DSN=https://<key>@sentry.io/<project>
```

---

## 6. Launch Production Stack

Run the stack with the production compose override:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Verify Service Status:
```bash
docker compose ps
```
All containers should be `Up` and healthy:
- `fpolink-postgres-1`
- `fpolink-backend-1`
- `fpolink-worker-1`
- `fpolink-frontend-1`
- `fpolink-tunnel-1`

### Run Database Migrations & Initial Seed:
```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed.py
```

---

## 7. Verification & Meta Webhook Wiring

### Step 1: Test External Health
From your local machine or terminal:
```bash
curl -i https://api.yourfpo.org/api/health
```
Expected output:
```json
HTTP/2 200
content-type: application/json

{"status":"ok","service":"fpolink-api","version":"0.1.0","db":"ok"}
```

### Step 2: Configure Meta WhatsApp Webhook
1. Go to [developers.facebook.com](https://developers.facebook.com/apps/) > Your App > **WhatsApp** > **Configuration**.
2. **Callback URL**: `https://api.yourfpo.org/api/whatsapp/webhook`
3. **Verify Token**: paste your `WHATSAPP_VERIFY_TOKEN` from `.env`.
4. Click **Verify and Save**.
5. Under **Webhook fields**, click **Manage** and subscribe to **`messages`**.

---

## 8. Automated Systemd Boot Service

To ensure FPOLink restarts automatically upon host reboot:

Create `/etc/systemd/system/fpolink.service`:
```ini
[Unit]
Description=FPOLink TN Production Stack
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/FPOLink
ExecStart=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fpolink.service
```

---

## 9. Backup & Maintenance

### Daily Automated Database Backup
Add a daily cron job on the host:
```bash
sudo crontab -e
```
Add the following line (runs at 02:00 UTC daily):
```cron
0 2 * * * docker compose -f /opt/FPOLink/docker-compose.yml exec -T postgres pg_dump -U fpolink_prod fpolink_prod | gzip > /opt/backups/fpolink_$(date +\%Y\%m\%d).sql.gz
```

### Emergency Halt
If you need to halt the bot immediately without downtime on the dashboard:
```bash
# In /opt/FPOLink/.env, set:
WHATSAPP_ENABLED=false
# Then restart backend and worker:
docker compose restart backend worker
```
