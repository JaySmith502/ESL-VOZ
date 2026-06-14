# ESL-voice Setup Workflow

This guide walks through every external platform, account, API key, and configuration step needed to run ESL-voice locally and in production.

## Accounts and platforms

Create accounts on the platforms you plan to use. Only the first four are required for M1; the AI vendors are optional because the voice tutor falls back to deterministic scoring when keys are absent.

| Platform | Purpose | Required for M1 |
|---|---|---|
| **GitHub** | Source control and CI/CD (`/.github/workflows`) | Yes |
| **VPS / cloud host** | Production server (Hetzner, DigitalOcean, AWS, etc.) | Yes |
| **Domain registrar** | Public domain and DNS (Porkbun, Cloudflare Registrar, Namecheap, etc.) | Yes |
| **Resend** | Transactional email / magic links | Yes |
| **Anthropic** | LLM correction feedback (`claude-3-haiku/sonnet`) | No |
| **OpenAI** | Text-to-speech (`tts-1`) | No |
| **Deepgram** | Speech-to-text (`nova-2`) | No |

## Local development setup

### 1. Clone the repository

```bash
git clone git@github.com:YOUR_ORG/esl-voice.git
cd esl-voice
```

### 2. Install tools

- Python 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 20 + npm
- Docker Desktop or Docker Engine

### 3. Backend dependencies

```bash
cd backend
uv sync --extra dev
```

### 4. Frontend dependencies

```bash
cd ../frontend
npm install
```

### 5. Environment file

Copy the example file and fill in the values:

```bash
cp .env.example .env
```

```bash
# .env — local development
DATABASE_URL=postgresql+asyncpg://eslvoice:eslvoice@localhost:5432/eslvoice
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=generate-a-random-string-here
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
RESEND_API_KEY=re_xxxxxxxx
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxx
DEEPGRAM_API_KEY=xxxxxxxx
```

Generate a secret key locally:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 6. Start backing services

```bash
make db
```

This starts Postgres + pgvector and Redis, runs Alembic migrations, and seeds the lesson catalog.

### 7. Start dev servers

```bash
make dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## External platform configuration

### Resend (email / magic links)

1. Sign up at https://resend.com
2. Add and verify a sending domain (e.g., `mail.yourdomain.com`).
3. Create an API key and copy it into `.env` as `RESEND_API_KEY`.
4. Update the from-address in `backend/app/services/auth.py` if it differs from the default.

### Anthropic (optional)

1. Sign up at https://console.anthropic.com
2. Create an API key under Settings → API keys.
3. Paste it into `.env` as `ANTHROPIC_API_KEY`.

### OpenAI (optional)

1. Sign up at https://platform.openai.com
2. Create a project API key and add billing.
3. Paste it into `.env` as `OPENAI_API_KEY`.

### Deepgram (optional)

1. Sign up at https://console.deepgram.com
2. Create a new project and copy the API key.
3. Paste it into `.env` as `DEEPGRAM_API_KEY`.

## Production deployment

### 1. Provision a server

Recommended minimum specs:

- 2 vCPU
- 4 GB RAM
- 40 GB SSD
- Ubuntu 24.04 LTS

Open firewall ports:

- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)

### 2. Point DNS to the server

At your domain registrar or DNS provider, create an A record:

```
A  yourdomain.com  <server-ip>
A  www.yourdomain.com  <server-ip>
```

If you want a separate email sending subdomain:

```
CNAME  mail.yourdomain.com  →  resend.
```

### 3. Install Docker on the server

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

Log out and back in for the group change to take effect.

### 4. Deploy the application

On your local machine:

```bash
# Add the server as a git remote (one-time)
git remote add prod ssh://$USER@<server-ip>/opt/esl-voice

# Push code
ssh $USER@<server-ip> "sudo mkdir -p /opt/esl-voice && sudo chown $USER:$USER /opt/esl-voice"
git push prod main
```

On the server:

```bash
cd /opt/esl-voice
cp .env.example .env
# edit .env with production secrets
make prod
```

`make prod` builds and starts the production Docker Compose stack.

### 5. SSL / HTTPS

For a production domain you should terminate TLS. Two common options:

**Option A — Let’s Encrypt with certbot on the host**

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

Copy or symlink the certificates to `infra/nginx/ssl/` and update `infra/nginx/nginx.conf` to listen on 443 with `ssl_certificate` and `ssl_certificate_key`.

**Option B — Cloudflare origin certificates**

If you proxy through Cloudflare, generate an origin certificate in the Cloudflare dashboard and place it in `infra/nginx/ssl/`.

### 6. Systemd auto-start (optional but recommended)

```bash
sudo cp infra/systemd/esl-voice.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable esl-voice.service
sudo systemctl start esl-voice.service
```

## GitHub Actions secrets

For automated CI/CD, add these secrets in your GitHub repository:

| Secret | Value |
|---|---|
| `PROD_HOST` | Production server IP or hostname |
| `PROD_USER` | SSH username on the production server |
| `PROD_SSH_KEY` | Private SSH key with push + deploy access |

## Verification checklist

After setup, confirm each piece works:

- [ ] `make test-backend` passes
- [ ] `make test-acceptance` passes
- [ ] `make lint-content` passes
- [ ] Frontend builds: `cd frontend && npm run build`
- [ ] Backend starts: `cd backend && uvicorn app.main:app`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] Magic-link email arrives when registering
- [ ] A learner can complete intake → placement → lesson → dashboard
- [ ] An instructor can view cohorts and flag a student
- [ ] Production domain serves the app over HTTPS

## Ongoing maintenance

- Rotate `SECRET_KEY` immediately after first production deploy.
- Keep Docker images updated: `docker compose -f infra/docker-compose.prod.yml pull && make prod`.
- Monitor Resend, Anthropic, OpenAI, and Deepgram usage dashboards for cost spikes.
- Back up the Postgres volume regularly (`infra/docker-compose.prod.yml` uses the `postgres_data` Docker volume).
