"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Script de gestion (Migrations, etc.)
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    from flask.cli import FlaskGroup
    cli = FlaskGroup(create_app=lambda: app)
    cli()
