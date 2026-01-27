"""
 * Nom de l'application : DISPARUS.ORG
 * Description : Script d'initialisation des donnees de demonstration
 * Produit de : MOA Digital Agency, www.myoneart.com
 * Fait par : Aisance KALONJI, www.aisancekalonji.com
 * Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
#!/usr/bin/env python3
"""
Script d'initialisation des donnees demo pour DISPARUS.ORG
Cree des profils de demonstration pour le Maroc et le Gabon
"""

import os
import sys
import random
import string
from datetime import datetime, timedelta

def generate_public_id():
    """Genere un ID public unique de 6 caracteres"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


DEMO_DATA = [
    # MAROC - Marrakech
    {
        'public_id': 'DEMO01',
        'person_type': 'adult',
        'first_name': 'Fatima',
        'last_name': 'El Mansouri',
        'age': 34,
        'sex': 'female',
        'country': 'Maroc',
        'city': 'Marrakech',
        'latitude': 31.6295,
        'longitude': -7.9811,
        'physical_description': 'Femme de taille moyenne (1m65), cheveux noirs longs, yeux marron fonce. Cicatrice au niveau du menton. Porte souvent un foulard beige.',
        'circumstances': 'Vue pour la derniere fois au souk de Marrakech pres de la place Jemaa el-Fna. Elle devait rentrer chez elle apres ses courses mais n\'est jamais arrivee.',
        'clothing': 'Robe traditionnelle verte, sandales marron',
        'objects': 'Sac a main en cuir rouge, telephone portable Samsung',
        'contacts': [{'name': 'Ahmed El Mansouri', 'phone': '+212 6 12 34 56 78', 'relation': 'epoux'}],
        'photo_url': None,
        'is_demo': True
    },
    {
        'public_id': 'DEMO02',
        'person_type': 'child',
        'first_name': 'Youssef',
        'last_name': 'Bennani',
        'age': 8,
        'sex': 'male',
        'country': 'Maroc',
        'city': 'Marrakech',
        'latitude': 31.6340,
        'longitude': -7.9956,
        'physical_description': 'Petit garcon, cheveux courts noirs, grands yeux noirs, teint mate. Tache de naissance sur l\'epaule droite.',
        'circumstances': 'Disparu lors d\'une sortie scolaire au jardin Majorelle. Ses camarades l\'ont vu pour la derniere fois pres de la fontaine.',
        'clothing': 'Uniforme scolaire bleu, baskets blanches Nike',
        'objects': 'Sac a dos Spiderman rouge et bleu',
        'contacts': [{'name': 'Khadija Bennani', 'phone': '+212 6 23 45 67 89', 'relation': 'mere'}],
        'photo_url': '/statics/uploads/demo/demo_child_male.jpg',
        'is_demo': True
    },
    # MAROC - Casablanca
    {
        'public_id': 'DEMO03',
        'person_type': 'adult',
        'first_name': 'Mohammed',
        'last_name': 'Alaoui',
        'age': 45,
        'sex': 'male',
        'country': 'Maroc',
        'city': 'Casablanca',
        'latitude': 33.5731,
        'longitude': -7.5898,
        'physical_description': 'Homme corpulent (1m78, environ 90kg), cheveux grisonnants, moustache noire, porte des lunettes de vue rectangulaires.',
        'circumstances': 'N\'est pas rentre du travail. Sa voiture a ete retrouvee pres du port de Casablanca.',
        'clothing': 'Costume gris, chemise blanche, cravate bleue',
        'objects': 'Mallette noire en cuir, montre Casio argentee',
        'contacts': [{'name': 'Sara Alaoui', 'phone': '+212 6 34 56 78 90', 'relation': 'fille'}],
        'photo_url': '/statics/uploads/demo/demo_adult_male.jpg',
        'is_demo': True
    },
    {
        'public_id': 'DEMO04',
        'person_type': 'elderly',
        'first_name': 'Aicha',
        'last_name': 'Tahiri',
        'age': 72,
        'sex': 'female',
        'country': 'Maroc',
        'city': 'Casablanca',
        'latitude': 33.5950,
        'longitude': -7.6187,
        'physical_description': 'Femme agee de petite taille (1m55), cheveux blancs, rides prononcees, utilise une canne pour marcher. Problemes de memoire.',
        'circumstances': 'Souffre d\'Alzheimer. Est sortie de la maison familiale pendant que sa famille dormait. N\'a pas ete revue depuis.',
        'clothing': 'Djellaba blanche, babouches jaunes',
        'objects': 'Bracelet medical avec son nom',
        'contacts': [{'name': 'Omar Tahiri', 'phone': '+212 6 45 67 89 01', 'relation': 'fils'}],
        'photo_url': None,
        'is_demo': True
    },
    # GABON - Port-Gentil
    {
        'public_id': 'DEMO05',
        'person_type': 'adult',
        'first_name': 'Jean-Pierre',
        'last_name': 'Moussavou',
        'age': 38,
        'sex': 'male',
        'country': 'Gabon',
        'city': 'Port-Gentil',
        'latitude': -0.7193,
        'longitude': 8.7815,
        'physical_description': 'Homme de grande taille (1m85), peau noire, crane rase, barbe courte. Tatouage d\'un lion sur l\'avant-bras gauche.',
        'circumstances': 'Travailleur sur une plateforme petroliere. N\'est jamais arrive a l\'heliport pour son transfert. Derniere localisation connue au port.',
        'clothing': 'Combinaison de travail orange, bottes de securite',
        'objects': 'Badge d\'acces Total, telephone Huawei',
        'contacts': [{'name': 'Marie Moussavou', 'phone': '+241 07 12 34 56', 'relation': 'epouse'}],
        'photo_url': '/statics/uploads/demo/demo_adult_male_2.jpg',
        'is_demo': True
    },
    {
        'public_id': 'DEMO06',
        'person_type': 'teenager',
        'first_name': 'Nadege',
        'last_name': 'Obiang',
        'age': 16,
        'sex': 'female',
        'country': 'Gabon',
        'city': 'Port-Gentil',
        'latitude': -0.7250,
        'longitude': 8.7720,
        'physical_description': 'Adolescente mince (1m60), cheveux tresses avec perles colorees, grain de beaute sur la joue gauche.',
        'circumstances': 'Partie au lycee le matin et n\'est jamais revenue. Ses amies disent qu\'elle a quitte l\'ecole a midi.',
        'clothing': 'Uniforme scolaire blanc et bleu, sac a dos rose',
        'objects': 'Telephone iPhone avec coque leopard',
        'contacts': [{'name': 'Paul Obiang', 'phone': '+241 06 23 45 67', 'relation': 'pere'}],
        'photo_url': None,
        'is_demo': True
    },
    # GABON - Libreville
    {
        'public_id': 'DEMO07',
        'person_type': 'adult',
        'first_name': 'Sylvie',
        'last_name': 'Nzoghe',
        'age': 29,
        'sex': 'female',
        'country': 'Gabon',
        'city': 'Libreville',
        'latitude': 0.4162,
        'longitude': 9.4673,
        'physical_description': 'Femme de taille moyenne (1m68), peau claire, cheveux defrises mi-longs, yeux noisette.',
        'circumstances': 'Sortie d\'un restaurant du centre-ville tard dans la soiree. Son taxi n\'est jamais arrive a destination.',
        'clothing': 'Robe rouge, talons noirs, veste en jean',
        'objects': 'Sac a main Gucci imitation, cles de voiture Toyota',
        'contacts': [{'name': 'Estelle Nzoghe', 'phone': '+241 05 34 56 78', 'relation': 'soeur'}],
        'photo_url': '/statics/uploads/demo/demo_adult_female.jpg',
        'is_demo': True
    },
    {
        'public_id': 'DEMO08',
        'person_type': 'child',
        'first_name': 'Kevin',
        'last_name': 'Mba',
        'age': 6,
        'sex': 'male',
        'country': 'Gabon',
        'city': 'Libreville',
        'latitude': 0.3901,
        'longitude': 9.4544,
        'physical_description': 'Petit garcon energique, cheveux courts, petite cicatrice au genou droit suite a une chute.',
        'circumstances': 'Jouait devant la maison familiale dans le quartier Akebe. Sa mere l\'a perdu de vue pendant quelques minutes.',
        'clothing': 'T-shirt jaune avec dessin de dinosaure, short bleu',
        'objects': 'Ballon de football',
        'contacts': [{'name': 'Christine Mba', 'phone': '+241 07 45 67 89', 'relation': 'mere'}],
        'photo_url': None,
        'is_demo': True
    }
]


def init_demo_data():
    """Initialise les donnees de demonstration dans la base de donnees"""
    
    from app import create_app
    from models import db
    from models.disparu import Disparu
    
    app = create_app()
    
    with app.app_context():
        print("Initialisation des donnees de demonstration...")
        
        created_count = 0
        skipped_count = 0
        
        for data in DEMO_DATA:
            existing = Disparu.query.filter_by(public_id=data['public_id']).first()
            if existing:
                print(f"  - {data['public_id']}: deja existe, ignore")
                skipped_count += 1
                continue
            
            days_ago = random.randint(1, 60)
            disappearance_date = datetime.now() - timedelta(days=days_ago)
            
            disparu = Disparu()
            disparu.public_id = data['public_id']
            disparu.person_type = data['person_type']
            disparu.first_name = data['first_name']
            disparu.last_name = data['last_name']
            disparu.age = data['age']
            disparu.sex = data['sex']
            disparu.country = data['country']
            disparu.city = data['city']
            disparu.latitude = data['latitude']
            disparu.longitude = data['longitude']
            disparu.physical_description = data['physical_description']
            disparu.circumstances = data['circumstances']
            disparu.clothing = data['clothing']
            disparu.objects = data['objects']
            disparu.contacts = data['contacts']
            disparu.photo_url = data['photo_url']
            disparu.disappearance_date = disappearance_date
            disparu.status = 'missing'
            disparu.is_flagged = False
            
            db.session.add(disparu)
            created_count += 1
            print(f"  + {data['public_id']}: {data['first_name']} {data['last_name']} ({data['city']}, {data['country']})")
        
        db.session.commit()
        
        print(f"\nTermine: {created_count} profils crees, {skipped_count} ignores")
        print("\nPays couverts:")
        print("  - Maroc: Marrakech, Casablanca")
        print("  - Gabon: Port-Gentil, Libreville")
        
        return created_count


def delete_demo_data():
    """Supprime toutes les donnees de demonstration"""
    
    from app import create_app
    from models import db
    from models.disparu import Disparu
    from models.contribution import Contribution
    from models.user import ModerationReport
    
    app = create_app()
    
    with app.app_context():
        print("Suppression des donnees de demonstration...")
        
        demo_ids = [d['public_id'] for d in DEMO_DATA]
        
        disparus = Disparu.query.filter(Disparu.public_id.in_(demo_ids)).all()
        disparu_db_ids = [d.id for d in disparus]
        
        if disparu_db_ids:
            contrib_deleted = Contribution.query.filter(Contribution.disparu_id.in_(disparu_db_ids)).delete(synchronize_session=False)
            report_deleted = ModerationReport.query.filter(
                ModerationReport.target_type == 'disparu',
                ModerationReport.target_id.in_(disparu_db_ids)
            ).delete(synchronize_session=False)
        else:
            contrib_deleted = 0
            report_deleted = 0
        
        disparu_deleted = Disparu.query.filter(Disparu.public_id.in_(demo_ids)).delete(synchronize_session=False)
        
        db.session.commit()
        
        print(f"\nTermine:")
        print(f"  - {disparu_deleted} profils demo supprimes")
        print(f"  - {contrib_deleted} contributions associees supprimees")
        print(f"  - {report_deleted} rapports de moderation supprimes")
        
        return disparu_deleted


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--delete':
        delete_demo_data()
    else:
        init_demo_data()
