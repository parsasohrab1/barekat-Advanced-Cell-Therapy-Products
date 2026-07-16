"""سرویس ذخیره‌سازی فایل‌ها در MinIO/S3."""

import io
import json
from pathlib import Path

import boto3
from botocore.client import Config

from barekat_cell_therapy.core.config import get_settings


class StorageService:
    """مدیریت پروفایل‌های ژنومی، طرح‌های CAR و پروتکل‌های تولید."""

    def __init__(self) -> None:
        settings = get_settings()
        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )

    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.client.create_bucket(Bucket=self.bucket)
            except Exception:
                pass

    def upload_bytes(
        self,
        data: bytes,
        object_key: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        try:
            self.ensure_bucket()
            self.client.upload_fileobj(
                io.BytesIO(data),
                self.bucket,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )
            return f"s3://{self.bucket}/{object_key}"
        except Exception:
            local_path = Path("data/uploads") / object_key
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(data)
            return str(local_path.resolve())

    def upload_json(self, payload: dict | list, object_key: str) -> str:
        return self.upload_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            object_key,
            content_type="application/json",
        )

    def download_bytes(self, object_key: str) -> bytes:
        try:
            buffer = io.BytesIO()
            self.client.download_fileobj(self.bucket, object_key, buffer)
            return buffer.getvalue()
        except Exception:
            local_path = Path("data/uploads") / object_key
            return local_path.read_bytes()

    def download_json(self, object_key: str) -> dict | list:
        return json.loads(self.download_bytes(object_key).decode("utf-8"))

    def profile_key(self, patient_id: str) -> str:
        return f"profiles/{patient_id}.json"

    def car_design_key(self, design_id: str) -> str:
        return f"car-designs/{design_id}.json"

    def protocol_key(self, patient_id: str, design_id: str) -> str:
        return f"protocols/{patient_id}/{design_id}.json"

    def simulation_key(self, simulation_id: str) -> str:
        return f"simulations/{simulation_id}.json"


def get_storage() -> StorageService:
    return StorageService()
