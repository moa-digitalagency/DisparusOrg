"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Utilitaires d'internationalisation
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import json
import os

_translations = {}

def load_translations():
    global _translations
    if _translations:
        return

    # Assuming lang directory is at root, sibling to utils/
    lang_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang')

    for lang in ['fr', 'en']:
        try:
            file_path = os.path.join(lang_dir, f'{lang}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    _translations[lang] = json.load(f)
            else:
                 _translations[lang] = {}
        except Exception as e:
            print(f"Error loading translations for {lang}: {e}")
            _translations[lang] = {}

def get_translation(key, locale='fr'):
    load_translations()
    print(f"DEBUG: get_translation {key} {locale}")

    # Handle locale fallback
    if locale not in ['fr', 'en']:
        locale = 'fr'

    def lookup(lang, k):
        parts = k.split('.')
        value = _translations.get(lang, {})
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value

    value = lookup(locale, key)

    if value is not None and isinstance(value, str):
        return value

    # Fallback to English if not found in current locale
    if locale != 'en':
        value_en = lookup('en', key)
        if value_en is not None and isinstance(value_en, str):
            return value_en

    # Return key if not found
    return key
