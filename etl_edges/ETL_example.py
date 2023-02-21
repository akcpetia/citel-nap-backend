import sys
import json
import awswrangler as wr
import pandas as pd
from sqlalchemy import create_engine
import boto3
from urllib.parse import quote_plus
from awsglue.utils import getResolvedOptions


args = getResolvedOptions(sys.argv, ['password'])
password = args['password']

s3 = boto3.resource('s3')

engine = create_engine('postgresql://postgres:%s@dev-instance-1.cs8tfjz0ixzj.us-east-1.rds.amazonaws.com:5432/devices' % quote_plus(password))

# df = pd.read_sql_query('select * from edge', engine)

folder = 's3://citel-nap/velocloud/edges/2023-2-13'
fnames = wr.s3.list_objects(folder)

res_list = []

MAX_RECORDS = 500

for fname in fnames[:MAX_RECORDS]:
    content_object = s3.Object('citel-nap', "/".join(fname.split('/')[3:]))
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    
    for k, v in json_content.items():
        if type(json_content[k]) == dict:
            json_content[k] = json.dumps(json_content[k])
    
    res_list.append(json_content)

df_table = pd.DataFrame(res_list)

df_table.to_sql('edge', con=engine, schema='public', if_exists='replace')
