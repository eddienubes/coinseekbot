from config import config
from .s3_service import S3Service


class S3PrivateService(S3Service):
    def __init__(self):
        super().__init__(bucket_name=config.s3_private_bucket_name)
