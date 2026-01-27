"""
Nom de l'application : DISPARUS.ORG
Description : Plateforme citoyenne de signalement de personnes disparues en Afrique
Produit de : MOA Digital Agency, www.myoneart.com
Fait par : Aisance KALONJI, www.aisancekalonji.com
Auditer par : La CyberConfiance, www.cyberconfiance.com
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour acceder a cette page.', 'warning')
            return redirect(url_for('public.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour acceder a cette page.', 'warning')
            return redirect(url_for('public.login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Acces reserve aux administrateurs.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function


def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash


def generate_token(user_id):
    import secrets
    return secrets.token_urlsafe(32)


def verify_token(token):
    pass
