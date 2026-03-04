# DFC Tracking Backend

Backend for DFC Tracking — API built with FastAPI to ingest, process and serve DFC data.

## Fonctionnalités
- Authentification (JWT)
- Endpoints pour DFC, utilisateurs et uploads
- Traitement de fichiers (services/file_processing)
- Tests unitaires pytest

## Prérequis
- Python 3.9+
- Git
- (Optionnel) Docker

## Installation locale
1. Cloner le dépôt (si ce n'est pas déjà fait):

```bash
git clone https://github.com/elhanafifatimaezahra25/DFC_Tracking_Backend.git
cd DFC_Tracking_Backend
```

2. Créer et activer un environnement virtuel:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Installer les dépendances:

```bash
pip install -r requirements.txt
```

## Variables d'environnement
Configurer les variables suivantes selon votre environnement:
- `DATABASE_URL` — URL de la base de données (ex: sqlite:///./data.db ou postgres...)
- `SECRET_KEY` — clé pour signer les tokens JWT
- `ENV` — `development` ou `production`

Vous pouvez utiliser un fichier `.env` à la racine pour faciliter le développement.

## Lancer l'application

En développement (Uvicorn):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Les routes sont définies dans `routes/` et l'entrée se trouve dans `app/main.py`.

## Docker
1. Construire l'image:

```bash
docker build -t dfc-tracking-backend .
```

2. Lancer le conteneur:

```bash
docker run -e DATABASE_URL="sqlite:///./data.db" -e SECRET_KEY="votre_cle" -p 8000:8000 dfc-tracking-backend
```

## Tests
Exécuter les tests avec pytest:

```bash
pytest -q
```

## Structure du projet (essentiel)
- `app/` — point d'entrée et configuration FastAPI
- `routes/` — définitions des routes
- `models/`, `schemas/` — modèles et schémas
- `services/` — logique métier (ex: `file_processing`)
- `core/` — configuration et sécurité

## Contribuer
- Ouvrir une issue pour discuter des changements
- Faire une branche de travail, commit clair, puis PR

## Licence
Indiquez ici la licence (ex: MIT) ou ajoutez un fichier `LICENSE`.

## Contact
Pour questions, ouvrez une issue ou contactez le mainteneur du dépôt.
