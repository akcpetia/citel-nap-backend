from django.conf import settings
import json
import dotenv, datetime, boto3
from django.core.management.base import BaseCommand, CommandError

def load_velocloud_API_tokens():
    with open(settings.BASE_DIR / 'networkanalyzer' / 'network_apis' / "VCO - API Tokens.json", "r") as opf:
        return json.load(opf)

class S3Command(BaseCommand):
    def bucket_timestamp_date_now_credentials(self):
        aws_credentials = dotenv.dotenv_values(settings.BASE_DIR/'.env')
        credentials = load_velocloud_API_tokens()
        date_now = datetime.datetime.now()
        timestamp = date_now.timestamp()
        s3 = boto3.resource('s3', aws_access_key_id=aws_credentials["aws_access_key_id"], aws_secret_access_key=aws_credentials["aws_secret_access_key"])
        bucket = s3.Bucket('citel-nap')
        return (bucket, timestamp, date_now, credentials)
