import os
import difflib
import re
from PIL import Image
from models import Disparu
from flask import current_app

STOP_WORDS = {
    'le', 'la', 'les', 'l', 'un', 'une', 'des', 'du', 'de', 'd',
    'et', 'ou', 'a', 'au', 'aux', 'ce', 'cet', 'cette', 'ces',
    'est', 'sont', 'il', 'elle', 'ils', 'elles', 'je', 'tu', 'nous', 'vous',
    'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
    'qui', 'que', 'quoi', 'dont', 'ou', 'quand', 'comment', 'pour',
    'avec', 'sans', 'dans', 'sur', 'sous', 'par', 'en', 'vers', 'chez'
}

_HASH_CACHE = {}

def compute_image_hash(image_path):
    """
    Computes dHash (difference hash) for an image.
    Returns a hexadecimal string representing the hash.
    """
    if not image_path:
        return None

    # Check cache first
    if image_path in _HASH_CACHE:
        return _HASH_CACHE[image_path]

    try:
        # Resolve full path if relative
        if not os.path.isabs(image_path):
            # Assume relative to app root or static folder depending on context
            # image_path usually starts with /static/uploads/
            # Remove leading slash if present
            rel_path = image_path.lstrip('/')
            # Use current_app.root_path if available, otherwise assume current working directory
            if current_app:
                base_path = current_app.root_path
            else:
                base_path = os.getcwd()

            full_path = os.path.join(base_path, rel_path)
        else:
            full_path = image_path

        if not os.path.exists(full_path):
            return None

        with Image.open(full_path) as img:
            # 1. Resize to 9x8 (width=9, height=8) for dHash
            # Using LANCZOS (formerly ANTIALIAS) for better downscaling
            img = img.resize((9, 8), Image.Resampling.LANCZOS)
            # 2. Convert to grayscale
            img = img.convert("L")

            pixels = list(img.getdata())

            # 3. Compute differences between adjacent pixels
            difference = []
            for row in range(8):
                for col in range(8):
                    pixel_left = pixels[row * 9 + col]
                    pixel_right = pixels[row * 9 + col + 1]
                    difference.append(pixel_left > pixel_right)

            # 4. Convert binary array to hex string
            decimal_value = 0
            hex_string = []
            for index, value in enumerate(difference):
                if value:
                    decimal_value += 2**(index % 8)
                if (index % 8) == 7:
                    hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
                    decimal_value = 0

            img_hash = "".join(hex_string)
            _HASH_CACHE[image_path] = img_hash
            return img_hash

    except Exception as e:
        # print(f"Error hashing image {image_path}: {e}")
        return None

def compare_hashes(hash1, hash2):
    """
    Compares two image hashes (hex strings).
    Returns a similarity score between 0.0 and 1.0.
    """
    if not hash1 or not hash2:
        return 0.0

    if len(hash1) != len(hash2):
        return 0.0

    # Hamming distance
    distance = 0
    # Convert hex to int
    try:
        n1 = int(hash1, 16)
        n2 = int(hash2, 16)

        # XOR to find differing bits
        x = n1 ^ n2

        # Count set bits
        distance = bin(x).count('1')

        # Max distance is 64 bits for 8x8 hash
        max_distance = 64

        similarity = 1.0 - (distance / max_distance)
        return max(0.0, similarity)
    except ValueError:
        return 0.0

def text_similarity(str1, str2):
    """
    Computes similarity ratio between two strings using SequenceMatcher.
    Returns score 0.0 to 1.0.
    """
    if not str1 or not str2:
        return 0.0
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def description_similarity(desc1, desc2):
    """
    Computes similarity based on keyword intersection.
    """
    if not desc1 or not desc2:
        return 0.0

    def tokenize(text):
        # Simple tokenization: remove punctuation, split by space
        words = re.findall(r'\w+', text.lower())
        return set(w for w in words if w not in STOP_WORDS and len(w) > 2)

    set1 = tokenize(desc1)
    set2 = tokenize(desc2)

    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    # Jaccard index
    return intersection / union if union > 0 else 0.0

def find_potential_matches(disparu):
    """
    Finds potential matches for a given Disparu object.
    Returns a list of dictionaries with 'disparu' (dict), 'score', and 'match_reasons'.
    """
    matches = []
    
    # Query other missing persons (or found ones, depending on use case)
    # Usually we want to match against ALL other records to find duplicates or matches across status
    # But for efficiency we might limit. The original code limited to status='missing' and id != disparu.id.
    # I will stick to id != disparu.id.
    
    # Check if we are in an application context to access DB
    # If not, return empty list (fail safe)
    try:
        query = Disparu.query.filter(Disparu.id != disparu.id)
        # Limiting to last 500
        all_disparus = query.limit(500).all()
    except Exception:
        return []

    # Calculate scores
    disparu_hash = None
    if disparu.photo_url:
        disparu_hash = compute_image_hash(disparu.photo_url)

    for other in all_disparus:
        score = 0
        reasons = []
        
        # 1. Location (Country & City) - Weight: High
        # Country
        if disparu.country and other.country:
            if disparu.country.lower() == other.country.lower():
                score += 15
                reasons.append("Pays identique")
        
        # City
        city_sim = text_similarity(disparu.city, other.city)
        if city_sim > 0.8:
            score += 15
            reasons.append(f"Ville similaire ({int(city_sim*100)}%)")

        # 2. Names (First & Last) - Weight: High
        # Check cross match (first-first vs first-last in case of swap)
        name1 = f"{disparu.first_name} {disparu.last_name}"
        name2 = f"{other.first_name} {other.last_name}"
        name3 = f"{other.last_name} {other.first_name}" # Swapped
        
        name_sim = max(text_similarity(name1, name2), text_similarity(name1, name3))
        if name_sim > 0.85:
            score += 30
            reasons.append(f"Nom très similaire ({int(name_sim*100)}%)")
        elif name_sim > 0.6:
            score += 15
            reasons.append(f"Nom similaire ({int(name_sim*100)}%)")

        # 3. Age - Weight: Medium/High
        if disparu.age and other.age and disparu.age > 0 and other.age > 0:
            age_diff = abs(disparu.age - other.age)
            if age_diff <= 2:
                score += 15
                reasons.append("Age proche (<= 2 ans)")
            elif age_diff <= 5:
                score += 10
                reasons.append("Age proche (<= 5 ans)")
        
        # 4. Sex - Weight: Medium (Filter?)
        if disparu.sex and other.sex and disparu.sex == other.sex:
            score += 10
        
        # 5. Physical Description - Weight: Medium
        desc_sim = description_similarity(disparu.physical_description, other.physical_description)
        if desc_sim > 0.3:
            points = int(desc_sim * 20) # Max 20 points
            score += points
            reasons.append(f"Description similaire ({int(desc_sim*100)}%)")

        # 6. Image - Weight: Very High
        if disparu_hash and other.photo_url:
            other_hash = compute_image_hash(other.photo_url)
            if other_hash:
                img_sim = compare_hashes(disparu_hash, other_hash)
                if img_sim > 0.8: # Threshold for high similarity
                    score += 40
                    reasons.append(f"Photo très similaire ({int(img_sim*100)}%)")
                elif img_sim > 0.6:
                    score += 20
                    reasons.append(f"Photo similaire ({int(img_sim*100)}%)")

        if score >= 30: # Threshold to be considered a match
            matches.append({
                'disparu': other.to_dict(),
                'score': score,
                'match_reasons': reasons
            })
    
    # Sort by score desc
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:10]

def find_similar_photos(photo_path, threshold=0.8):
    return []

def compare_photos(photo1_path, photo2_path):
    h1 = compute_image_hash(photo1_path)
    h2 = compute_image_hash(photo2_path)
    return compare_hashes(h1, h2)

def extract_features(photo_path):
    return compute_image_hash(photo_path)
