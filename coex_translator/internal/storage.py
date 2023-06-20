import dataclasses
import io
import typing

import boto3
import botocore.exceptions
from django.conf import settings


class S3Storage:
    class ConnectionError(Exception):
        pass

    @dataclasses.dataclass
    class ObjectNotFoundError(Exception):
        msg: str
        path: str

    def __init__(
            self,
            access_key_id: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_ACCESS_KEY_ID,
            secret_access_key: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_SECRET_ACCESS_KEY,
            region_name: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_REGION_NAME,
            endpoint_url: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_ENDPOINT_URL,
    ):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url

    def upload(
            self,
            obj: typing.BinaryIO,
            destination: str,
            bucket_name: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_BUCKET_NAME,
            acl: str = "public-read",
            content_type: str = 'application/json',
            extra_args: typing.Optional[dict] = None,
    ) -> None:
        """
        Upload object to S3 bucket.
        :param obj: The object to upload.
        :param destination: A full destination path in the bucket. Example: 'translations/translations.json'.
        :param bucket_name: The name of the bucket to upload to.
        :param acl: The ACL to apply to the object.
            See https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl.
        :param content_type: The content type of the object.
        :param extra_args: Extra arguments to pass to boto3's upload_fileobj method.
        """
        if extra_args is None:
            extra_args = {}
        self.client.upload_fileobj(
            Fileobj=obj,
            Key=destination,
            Bucket=bucket_name,
            ExtraArgs={"ACL": acl, "ContentType": content_type} | extra_args,
        )

    def download(
            self,
            origin: str,
            bucket_name: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_BUCKET_NAME,
    ) -> bytes:
        """
        Download object from S3 bucket.
        :param origin: A full path to the object in the bucket. Example: 'translations/translations.json'.
        :param bucket_name: The name of the bucket to download from.
        :raises: ConnectionError if the object is not found on given origin path.
        """
        buffer = io.BytesIO()
        try:
            self.client.download_fileobj(
                Bucket=bucket_name,
                Key=origin,
                Fileobj=buffer,
            )
        except botocore.exceptions.ClientError as e:
            if e.response.get('Error', {}).get("Code") == "404":
                raise self.ObjectNotFoundError(f"Object not found on path {origin}.", path=origin)
            raise self.ConnectionError(str(e))
        return buffer.getvalue()

    @property
    def client(self):  # Right now, impossible to type because of boto3 metaclass magic...
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
        )
