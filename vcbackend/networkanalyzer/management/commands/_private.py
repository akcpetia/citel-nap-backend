from django.conf import settings
import json

def load_velocloud_API_tokens():
    with open(settings.BASE_DIR / 'networkanalyzer' / 'network_apis' / "VCO - API Tokens.json", "r") as opf:
        return json.load(opf)
