from models import Disparu


def find_similar_photos(photo_path, threshold=0.8):
    return []


def compare_photos(photo1_path, photo2_path):
    return 0.0


def extract_features(photo_path):
    return []


def find_potential_matches(disparu):
    matches = []
    
    all_disparus = Disparu.query.filter(
        Disparu.id != disparu.id,
        Disparu.status == 'missing'
    ).all()
    
    desc1_words = None
    if disparu.physical_description:
        desc1_words = set(disparu.physical_description.lower().split())

    for other in all_disparus:
        score = 0
        
        if disparu.age and other.age:
            age_diff = abs(disparu.age - other.age)
            if age_diff <= 5:
                score += 20
            elif age_diff <= 10:
                score += 10
        
        if disparu.sex == other.sex:
            score += 15
        
        if disparu.country == other.country:
            score += 10
            if disparu.city == other.city:
                score += 15
        
        if desc1_words and other.physical_description:
            desc2_words = set(other.physical_description.lower().split())
            common_words = desc1_words & desc2_words
            if len(common_words) >= 5:
                score += 20
        
        if score >= 30:
            matches.append({
                'disparu': other.to_dict(),
                'score': score,
                'match_reasons': []
            })
    
    return sorted(matches, key=lambda x: x['score'], reverse=True)[:10]
