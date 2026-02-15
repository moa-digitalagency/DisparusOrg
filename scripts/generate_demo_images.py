#!/usr/bin/env python3
"""
Generate demo profile images for DISPARUS.ORG
Creates simple placeholder images for demo profiles
"""

import os
from PIL import Image, ImageDraw, ImageFont

DEMO_FOLDER = 'static/uploads/demo'

DEMO_IMAGES = [
    {
        'filename': 'demo_child_male.jpg',
        'label': 'DEMO',
        'sublabel': 'Enfant',
        'bg_color': '#3B82F6',
        'text_color': '#FFFFFF'
    },
    {
        'filename': 'demo_adult_male.jpg',
        'label': 'DEMO',
        'sublabel': 'Homme',
        'bg_color': '#1E40AF',
        'text_color': '#FFFFFF'
    },
    {
        'filename': 'demo_adult_male_2.jpg',
        'label': 'DEMO',
        'sublabel': 'Homme 2',
        'bg_color': '#059669',
        'text_color': '#FFFFFF'
    },
    {
        'filename': 'demo_adult_female.jpg',
        'label': 'DEMO',
        'sublabel': 'Femme',
        'bg_color': '#DB2777',
        'text_color': '#FFFFFF'
    }
]


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_demo_image(config):
    """Generate a single demo image"""
    width, height = 400, 500
    bg_color = hex_to_rgb(config['bg_color'])
    text_color = hex_to_rgb(config['text_color'])
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    icon_y = height // 3
    icon_radius = 60
    draw.ellipse([width//2 - icon_radius, icon_y - icon_radius, 
                  width//2 + icon_radius, icon_y + icon_radius], 
                 fill=text_color)
    
    head_radius = 25
    draw.ellipse([width//2 - head_radius, icon_y - 45 - head_radius,
                  width//2 + head_radius, icon_y - 45 + head_radius],
                 fill=bg_color)
    
    draw.arc([width//2 - 35, icon_y - 20, width//2 + 35, icon_y + 40],
             0, 180, fill=bg_color, width=20)
    
    draw.text((width//2, height//2 + 40), config['label'], 
              fill=text_color, font=font_large, anchor='mm')
    
    draw.text((width//2, height//2 + 90), config['sublabel'],
              fill=text_color, font=font_medium, anchor='mm')
    
    draw.text((width//2, height - 30), 'disparus.org',
              fill=text_color, font=font_small, anchor='mm')
    
    return img


def generate_all_demo_images():
    """Generate all demo images"""
    os.makedirs(DEMO_FOLDER, exist_ok=True)
    
    print("Generation des images demo...")
    
    for config in DEMO_IMAGES:
        filepath = os.path.join(DEMO_FOLDER, config['filename'])
        img = generate_demo_image(config)
        img.save(filepath, 'JPEG', quality=90)
        print(f"  + {config['filename']} cree")
    
    print(f"\n{len(DEMO_IMAGES)} images demo generees dans {DEMO_FOLDER}/")


if __name__ == '__main__':
    generate_all_demo_images()
