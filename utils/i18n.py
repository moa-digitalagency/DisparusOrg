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

    # Try requested locale
    value = lookup(locale, key)

    if value is not None and isinstance(value, str):
        return value

    # Robust Fallback Strategy
    # If current locale is not 'fr', try falling back to 'fr' (primary language)
    # If current locale is 'fr', try falling back to 'en' (secondary language)
    fallback_locale = 'fr' if locale != 'fr' else 'en'

    value_fallback = lookup(fallback_locale, key)
    if value_fallback is not None and isinstance(value_fallback, str):
        return value_fallback

    # Return key if not found
    return key
