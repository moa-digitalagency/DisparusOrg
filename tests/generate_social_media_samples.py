import asyncio
import os
import sys
from datetime import datetime

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.pdf_gen import generate_social_media_image
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.pdf_gen import generate_social_media_image

class MockDisparu:
    def __init__(self, **kwargs):
        self.public_id = "GEN001"
        self.first_name = "Jean"
        self.last_name = "Dupont"
        self.age = 30
        self.sex = "male"
        self.person_type = "adult"
        self.city = "Paris"
        self.country = "France"
        self.physical_description = "Un homme de taille moyenne, cheveux bruns."
        self.photo_url = None
        self.disappearance_date = datetime.now()
        self.updated_at = datetime.now()
        self.contacts = [{"name": "Police", "phone": "17"}]
        self.status = "missing"

        for k, v in kwargs.items():
            setattr(self, k, v)

async def generate_all():
    output_dir = "generated_samples"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Generating samples in {output_dir}...")

    # Define the 4 states and their data
    states = [
        {"status": "missing", "name": "Missing", "data": {"status": "missing", "sex": "male", "person_type": "adult"}},
        {"status": "found_alive", "name": "Found_Alive", "data": {"status": "found_alive", "sex": "female", "person_type": "adult"}},
        {"status": "found_deceased", "name": "Found_Deceased", "data": {"status": "found_deceased", "sex": "male", "person_type": "adult"}},
        {"status": "found_injured", "name": "Found_Injured", "data": {"status": "found_injured", "sex": "female", "person_type": "adult"}}
    ]

    # Also include Animal variants for completeness if desired, but 4 states was the request.
    # The 4 main states are: Missing, Found Alive, Found Deceased, Injured.

    locales = ['fr', 'en']

    for state in states:
        for loc in locales:
            d = MockDisparu(**state["data"])
            filename = f"{state['name']}_{loc}.png"
            print(f"Generating {filename}...")
            img = await generate_social_media_image(d, locale=loc)

            if img:
                with open(f"{output_dir}/{filename}", "wb") as f:
                    f.write(img.read())
                print(f" -> Success: {filename}")
            else:
                print(f" -> FAILED: {filename}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_all())
