# DevOps Monitoring Dashboard

## Setup local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'API

```bash
uvicorn api.main:app --reload --port 8000
```

API docs : http://localhost:8000/docs

## Lancer le dashboard Streamlit

```bash
streamlit run dashboard/app.py
```

## Lancer les tests

```bash
pytest tests/ -v
pytest tests/ --cov=api  # avec coverage
```

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `API_KEY` | `dev-secret` | Clé API pour les endpoints protégés |