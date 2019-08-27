from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class S3MediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    default_acl = settings.AWS_DEFAULT_ACL
    location = settings.MEDIAFILES_LOCATION
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    file_overwrite = False
