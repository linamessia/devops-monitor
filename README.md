# DevOps Monitoring Dashboard

Système de monitoring temps réel construit en Python, containerisé avec Docker et déployé sur Azure via GitHub Actions.

## Architecture

```
FastAPI (port 8000)          Streamlit (port 8501)
├── GET  /health             ├── Onglet Métriques (CPU, RAM, Disk)
├── GET  /metrics            └── Onglet Serveurs (CRUD + health check)
├── WS   /ws/metrics
├── POST /servers
├── GET  /servers
├── DELETE /servers/{id}
└── POST /servers/{id}/check
```

## Prérequis

- Python 3.11
- Docker + Docker Compose
- Make

## Lancement local (avec Docker)

```bash
git clone <url-du-repo>
cd devops-monitor
cp .env.example .env   # remplir les valeurs
make up                # démarre la stack
make test              # lance les tests
```

- API : http://localhost:8000/docs
- Dashboard : http://localhost:8501

## Lancement local (sans Docker)

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
streamlit run dashboard/app.py
```

## Commandes Make

| Commande | Description |
|----------|-------------|
| `make up` | Démarre la stack Docker |
| `make down` | Arrête les conteneurs |
| `make logs` | Affiche les logs |
| `make test` | Lance les tests avec coverage |
| `make lint` | Lance flake8 |
| `make dev` | Lance sans Docker |

## Variables d'environnement

| Variable | Description |
|----------|-------------|
| `API_KEY` | Clé d'accès pour les endpoints protégés |
| `API_BASE_URL` | URL de l'API vue par le dashboard |

## URLs live (Azure)

- API : `https://<api>.<env>.azurecontainerapps.io/docs`
- Dashboard : `https://<dashboard>.<env>.azurecontainerapps.io`