"""Provision this project's minimal AWS resources and deploy a prebuilt static bundle.

Usage: python infrastructure/deploy_aws.py prepare|publish|status
Requires an authenticated karachi-pulse AWS profile. Never prints API keys or signed URLs.
"""
import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import requests
from botocore.config import Config
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.tools/deployment-state.json'
REGION = 'ap-south-1'
PROJECT = 'karachi-pulse'
BRANCH = 'main'
CONFIG = Config(retries={'total_max_attempts': 3, 'mode': 'standard'}, connect_timeout=10, read_timeout=60)

def save(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')

def session():
    return boto3.Session(profile_name=PROJECT, region_name=REGION)

def client(name):
    config = CONFIG.merge(Config(signature_version='s3v4')) if name == 's3' else CONFIG
    endpoint={'endpoint_url':f'https://s3.{REGION}.amazonaws.com'} if name == 's3' else {}
    return session().client(name, config=config, **endpoint)

def state_file():
    return json.loads(STATE.read_text()) if STATE.exists() else {}

def prepare():
    state = state_file()
    account = client('sts').get_caller_identity()['Account']
    if state.get('account') not in (None, account):
        raise RuntimeError('Deployment state belongs to a different AWS account')
    state.update(account=account, region=REGION)
    amplify = client('amplify')
    if not state.get('app_id'):
        existing = [app for page in amplify.get_paginator('list_apps').paginate() for app in page['apps'] if app['name'] == PROJECT]
        if existing:
            raise RuntimeError('An app with this name exists without matching local deployment state; inspect before reusing')
        app = amplify.create_app(name=PROJECT, platform='WEB', description='Karachi healthcare infrastructure explorer', tags={'Project': PROJECT})['app']
        state.update(app_id=app['appId'], default_domain=app['defaultDomain'])
        save(state)
    branches = amplify.list_branches(appId=state['app_id'])['branches']
    if not any(b['branchName'] == BRANCH for b in branches):
        amplify.create_branch(appId=state['app_id'], branchName=BRANCH, stage='PRODUCTION', enableAutoBuild=False, framework='React')
    state['url'] = f"https://{BRANCH}.{state['default_domain']}"
    save(state)
    location = client('location')
    if not state.get('map_arn'):
        existing = [m for page in location.get_paginator('list_maps').paginate() for m in page['Entries'] if m['MapName'] == PROJECT]
        if existing:
            raise RuntimeError('Map name already exists without matching local state; refusing to overwrite')
        result = location.create_map(MapName=PROJECT, Configuration={'Style':'VectorEsriDarkGrayCanvas'}, PricingPlan='RequestBasedUsage', Description='Karachi Pulse healthcare overlays', Tags={'Project': PROJECT})
        state['map_arn'] = result['MapArn']
        save(state)
    if not state.get('key_name'):
        state['key_name'] = f'{PROJECT}-web'
        # Do not reuse a pre-existing key that was not created in this deployment.
        existing_keys = location.list_keys()['Entries']
        if any(k['KeyName'] == state['key_name'] for k in existing_keys):
            raise RuntimeError('API key name already exists; inspect its ownership before continuing')
        expires = datetime.now(timezone.utc) + timedelta(days=90)
        location.create_key(KeyName=state['key_name'], Description='Map rendering only; exact map and app origins', ExpireTime=expires,
            Restrictions={'AllowActions':['geo:GetMap*'], 'AllowResources':[state['map_arn']], 'AllowReferers':[state['url']+'/*','http://127.0.0.1:5173/*']}, Tags={'Project':PROJECT})
        state['key_expires_at'] = expires.isoformat()
        save(state)
    key = location.describe_key(KeyName=state['key_name'])['Key']
    env = ROOT/'frontend/.env.local'
    existing_env = env.read_text(encoding='utf-8-sig').splitlines() if env.exists() else []
    replacements = {'VITE_AWS_REGION':REGION, 'VITE_LOCATION_MAP_NAME':PROJECT, 'VITE_LOCATION_API_KEY':key, 'VITE_DATA_URL':''}
    preserved = [line for line in existing_env if line.split('=',1)[0] not in replacements]
    env.write_text('\n'.join(preserved+[f'{k}={v}' for k,v in replacements.items()])+'\n', encoding='utf-8')
    s3 = client('s3')
    if not state.get('bucket'):
        bucket = f'{PROJECT}-data-{account}-{REGION}'
        names = [b['Name'] for b in s3.list_buckets()['Buckets']]
        if bucket in names:
            raise RuntimeError('Bucket already exists without matching deployment state')
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={'LocationConstraint':REGION}, ObjectOwnership='BucketOwnerEnforced')
        state['bucket'] = bucket
        save(state)
    bucket = state['bucket']
    s3.head_bucket(Bucket=bucket, ExpectedBucketOwner=account)
    s3.put_public_access_block(Bucket=bucket, ExpectedBucketOwner=account, PublicAccessBlockConfiguration={k:True for k in ['BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets']})
    s3.put_bucket_encryption(Bucket=bucket, ExpectedBucketOwner=account, ServerSideEncryptionConfiguration={'Rules':[{'ApplyServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]})
    s3.put_bucket_versioning(Bucket=bucket, ExpectedBucketOwner=account, VersioningConfiguration={'Status':'Enabled'})
    s3.put_bucket_tagging(Bucket=bucket, ExpectedBucketOwner=account, Tagging={'TagSet':[{'Key':'Project','Value':PROJECT}]})
    policy={'Version':'2012-10-17','Statement':[{'Sid':'DenyInsecureTransport','Effect':'Deny','Principal':'*','Action':'s3:*','Resource':[f'arn:aws:s3:::{bucket}',f'arn:aws:s3:::{bucket}/*'],'Condition':{'Bool':{'aws:SecureTransport':'false','aws:PrincipalIsAWSService':'false'}}}]}
    s3.put_bucket_policy(Bucket=bucket, ExpectedBucketOwner=account, Policy=json.dumps(policy))
    s3.put_bucket_cors(Bucket=bucket, ExpectedBucketOwner=account, CORSConfiguration={'CORSRules':[{'AllowedOrigins':[state['url'],'http://127.0.0.1:5173'],'AllowedMethods':['GET','HEAD'],'AllowedHeaders':['*'],'ExposeHeaders':['ETag'],'MaxAgeSeconds':3600}]})
    data=(ROOT/'data-pipeline/data/processed/facilities.geojson').read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    object_key=f'{PROJECT}/{digest}/facilities.geojson'
    try:
        s3.put_object(Bucket=bucket, Key=object_key, Body=data, ContentType='application/geo+json', ServerSideEncryption='AES256', ExpectedBucketOwner=account, IfNoneMatch='*')
    except ClientError as error:
        if error.response['Error']['Code'] != 'PreconditionFailed':
            raise
    # Production consumes a verified private-S3 snapshot at build time; no expiring URL is embedded.
    response=s3.get_object(Bucket=bucket, Key=object_key, ExpectedBucketOwner=account)
    with response['Body'] as body:
        downloaded=body.read()
    if hashlib.sha256(downloaded).hexdigest()!=digest:
        raise RuntimeError('Stored S3 snapshot does not match the validated source')
    (ROOT/'frontend/public/data/facilities.geojson').write_bytes(downloaded)
    signed=s3.generate_presigned_url('get_object',Params={'Bucket':bucket,'Key':object_key},ExpiresIn=300)
    response=requests.get(signed,headers={'Origin':state['url']},timeout=60)
    if response.status_code != 200 or hashlib.sha256(response.content).hexdigest()!=digest:
        from xml.etree import ElementTree
        try:
            failure=ElementTree.fromstring(response.content)
            reason=failure.findtext('Code')
        except ElementTree.ParseError:
            reason='unexpected_response'
        raise RuntimeError(f'Signed S3 read verification failed: HTTP {response.status_code}, {reason}')
    if response.headers.get('Access-Control-Allow-Origin') != state['url']:
        raise RuntimeError('S3 browser CORS verification failed')
    style_url=f'https://maps.geo.{REGION}.amazonaws.com/maps/v0/maps/{PROJECT}/style-descriptor'
    style_response=requests.get(style_url,params={'key':key},headers={'Referer':state['url']+'/'},timeout=30)
    if style_response.status_code != 200 or style_response.json().get('version') != 8:
        raise RuntimeError(f'Amazon Location style verification failed ({style_response.status_code})')
    state.update(dataset_key=object_key,dataset_sha256=digest,s3_read_verified=True,location_style_verified=True)
    save(state)
    print(json.dumps({k:v for k,v in state.items() if k not in ['account']},indent=2))

def publish():
    state=state_file()
    if not state.get('location_style_verified') or not state.get('s3_read_verified'):
        raise RuntimeError('Run prepare and complete AWS integration checks before publishing')
    dist=ROOT/'frontend/dist'
    if not (dist/'index.html').is_file():
        raise RuntimeError('Build the frontend before deploying')
    archive=ROOT/'.tools/amplify-deploy.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as zipped:
        for path in dist.rglob('*'):
            if path.is_file():
                zipped.write(path,path.relative_to(dist).as_posix())
    amplify=client('amplify')
    deployment=amplify.create_deployment(appId=state['app_id'],branchName=BRANCH)
    # Signed upload URLs remain only in process memory.
    response=requests.put(deployment['zipUploadUrl'],data=archive.read_bytes(),headers={'Content-Type':'application/zip'},timeout=120)
    if not response.ok:
        raise RuntimeError(f'Amplify archive upload failed ({response.status_code})')
    job=amplify.start_deployment(appId=state['app_id'],branchName=BRANCH,jobId=deployment['jobId'])['jobSummary']
    state.update(job_id=job['jobId'],deployment_status=job['status'])
    save(state)
    print(json.dumps({'url':state['url'],'job_id':state['job_id'],'status':job['status']}))

def status():
    state=state_file()
    job=client('amplify').get_job(appId=state['app_id'],branchName=BRANCH,jobId=state['job_id'])['job']['summary']
    state['deployment_status']=job['status']
    save(state)
    print(json.dumps({'url':state['url'],'job_id':state['job_id'],'status':job['status']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['prepare','publish','status'])
    {'prepare':prepare,'publish':publish,'status':status}[parser.parse_args().action]()
