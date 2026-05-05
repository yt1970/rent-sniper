"""
json_store.py - S3対応版
ローカルで動かす場合は json_store_local.py を使うこと
"""
import json
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET", "rent-sniper-data")
S3_KEY = os.getenv("S3_KEY", "rooms.json")

s3 = boto3.client("s3")


def load_previous() -> list[dict]:
    try:
        res = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return json.loads(res["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            print("S3: rooms.json not found, starting fresh.")
            return []
        raise


def save_current(data: list[dict]):
    body = json.dumps(data, indent=2, ensure_ascii=False)
    s3.put_object(Bucket=S3_BUCKET, Key=S3_KEY, Body=body.encode("utf-8"))
    print(f"S3: saved {len(data)} rooms to s3://{S3_BUCKET}/{S3_KEY}")


def diff_rooms(old: list[dict], new: list[dict]) -> list[dict]:
    old_ids = set(r["id"] for r in old)
    return [r for r in new if r["id"] not in old_ids]
