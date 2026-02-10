import asyncio
import os
import sys
from datetime import datetime

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.pdf_gen import generate_social_media_image
except ImportError:
    # Fallback if run directly from tests/
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.pdf_gen import generate_social_media_image

class MockDisparu:
    def __init__(self, **kwargs):
        self.public_id = "TEST001"
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

async def run_tests():
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Generating images in {output_dir}...")

    # 1. Missing (Red)
    print("1. Generating MISSING (Red)...")
    d1 = MockDisparu(status='missing', first_name="Paul", last_name="Missing")
    img1 = await generate_social_media_image(d1)
    if img1:
        with open(f"{output_dir}/missing.png", "wb") as f:
            f.write(img1.read())
        print(" -> Success: missing.png")
    else:
        print(" -> FAILED: missing.png")

    # 2. Found Alive (Green)
    print("2. Generating FOUND ALIVE (Green)...")
    d2 = MockDisparu(status='found_alive', first_name="Marie", last_name="Found", sex="female")
    img2 = await generate_social_media_image(d2)
    if img2:
        with open(f"{output_dir}/found_alive.png", "wb") as f:
            f.write(img2.read())
        print(" -> Success: found_alive.png")
    else:
        print(" -> FAILED: found_alive.png")

    # 3. Found Deceased (Gray)
    print("3. Generating DECEASED (Gray)...")
    d3 = MockDisparu(status='found_deceased', first_name="Jacques", last_name="Deceased", sex="male", person_type="elderly")
    img3 = await generate_social_media_image(d3)
    if img3:
        with open(f"{output_dir}/deceased.png", "wb") as f:
            f.write(img3.read())
        print(" -> Success: deceased.png")
    else:
        print(" -> FAILED: deceased.png")

    # 4. Found Injured (Orange)
    print("4. Generating INJURED (Orange)...")
    d4 = MockDisparu(status='found_injured', first_name="Rex", last_name="", sex="male", person_type="animal")
    img4 = await generate_social_media_image(d4)
    if img4:
        with open(f"{output_dir}/injured.png", "wb") as f:
            f.write(img4.read())
        print(" -> Success: injured.png")
    else:
        print(" -> FAILED: injured.png")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_tests())
