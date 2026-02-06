import os
import io
from flask import Flask
from app import create_app
from models import db
from services.analytics import get_platform_stats
from utils.pdf_gen import generate_statistics_pdf
from utils.i18n import get_translation

def generate_pdf():
    app = create_app()
    with app.app_context():
        # Get statistics (replicating _get_statistics_data minimal logic)
        from routes.admin import _get_statistics_data

        # Using default period 'all'
        data = _get_statistics_data('all')

        # Translation helper
        def t(key, **kwargs):
            text = get_translation(key, 'fr')
            if kwargs:
                try:
                    return text.format(**kwargs)
                except:
                    return text
            return text

        # Generate PDF
        print("Generating PDF...")
        pdf_buffer = generate_statistics_pdf(data, t, locale='fr')

        if pdf_buffer:
            output_path = 'statics/stats_test.pdf'
            os.makedirs('statics', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print(f"PDF generated successfully at {output_path}")
        else:
            print("Failed to generate PDF.")

if __name__ == "__main__":
    generate_pdf()
