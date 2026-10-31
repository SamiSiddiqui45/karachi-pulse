"""Explicit existing bucket only. Does not create resources or replace objects."""
import argparse
import hashlib
from pathlib import Path
import boto3
from botocore.config import Config
def upload(bucket,owner,region):
    root=Path(__file__).resolve().parents[2]
    env_path=root/"frontend/.env.s3.local"
    if env_path.exists(): raise RuntimeError("Review/remove the previous ignored .env.s3.local before generating a new URL")
    path=root/"data-pipeline/data/processed/facilities.geojson"
    s3=boto3.client("s3",region_name=region,endpoint_url=f"https://s3.{region}.amazonaws.com",config=Config(signature_version="s3v4"))
    s3.head_bucket(Bucket=bucket,ExpectedBucketOwner=owner)
    blocks=s3.get_public_access_block(Bucket=bucket,ExpectedBucketOwner=owner)["PublicAccessBlockConfiguration"]
    if not all(blocks.values()): raise RuntimeError("Enable all four S3 public access blocks first")
    key=f"karachi-pulse/{hashlib.sha256(path.read_bytes()).hexdigest()}/facilities.geojson"
    s3.put_object(Bucket=bucket,Key=key,Body=path.read_bytes(),ContentType="application/geo+json",ServerSideEncryption="AES256",ExpectedBucketOwner=owner,IfNoneMatch="*")
    print(f"Uploaded s3://{bucket}/{key}")
    url=s3.generate_presigned_url("get_object",Params={"Bucket":bucket,"Key":key},ExpiresIn=3600)
    env_path.write_text(f"VITE_DATA_URL={url}\n",encoding="utf-8")
    print("One-hour read URL saved to ignored frontend/.env.s3.local; run npm run dev -- --mode s3.")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--bucket",required=True)
    p.add_argument("--expected-owner",required=True)
    p.add_argument("--region",required=True)
    a=p.parse_args()
    upload(a.bucket,a.expected_owner,a.region)
