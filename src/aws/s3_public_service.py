from config import config
from .s3_service import S3Service


class S3PublicService(S3Service):
    def __init__(self):
        super().__init__(bucket_name=config.s3_public_bucket_name)
