# DISPARUS.ORG

Plateforme citoyenne centralisée pour la recherche de personnes et animaux disparus en Afrique.

## Documentation

Toute la documentation détaillée se trouve dans le dossier [`docs/`](./docs/README.md).

*   [Vision du Projet](./docs/VISION_PRODUIT.md)
*   [Architecture Technique](./docs/ARCHITECTURE_TECHNIQUE.md)
*   [Manuel Utilisateur](./docs/MANUEL_UTILISATEUR.md)
*   [Manuel Administration](./docs/MANUEL_ADMINISTRATION.md)

## Démarrage Rapide

### Prérequis
*   Python 3.10+
*   SQLite (Dev) / PostgreSQL (Prod)

### Installation

1.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

2.  Initialiser la base de données :
    ```bash
    python init_db.py
    ```

3.  Lancer l'application :
    ```bash
    python main.py
    ```

L'application sera accessible sur `http://localhost:5000`.

## Licence
Voir la documentation interne ou contacter les administrateurs.
