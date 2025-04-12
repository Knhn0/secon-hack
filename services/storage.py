import io
import zipfile
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from fastapi import UploadFile, File, HTTPException, status, Query
from starlette.responses import StreamingResponse

import config

s3_client = boto3.client(
    "s3",
    aws_access_key_id=config.S3_ACCESS_KEY_ID,  # замените на свой access key
    aws_secret_access_key=config.S3_SECRET_KEY,  # замените на свой secret key
    region_name="ru-msk",
    endpoint_url=config.S3_URL
)


class StorageService:
    async def upload_file(self, bucket_name: str, file: UploadFile = File(...)):
        try:
            content = await file.read()
            s3_client.put_object(Bucket=bucket_name, Key=file.filename, Body=content, ACL='public-read')
        except BotoCoreError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def generate_presigned_url(self, filename):
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': "secon2025",
                    'Key': filename,
                    'ResponseContentDisposition': f'attachment; filename="{filename}"'
                },
            )
            return url
        except NoCredentialsError:
            return "Ошибка: Учетные данные не найдены."

    async def download_archive(
            self,
            keys: list[str] = Query(
                ...,
                description="Список ключей файлов, которые необходимо включить в архив"
            )
    ):
        bucket_name = "secon2025"  # Имя вашего бакета в S3

        zip_in_memory = io.BytesIO()

        try:
            with zipfile.ZipFile(zip_in_memory, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                for key in keys:
                    try:
                        response = s3_client.get_object(Bucket=bucket_name, Key=key)
                        file_content = response["Body"].read()
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Не удалось получить файл '{key}': {e}"
                        )
                    filename_in_zip = key.split("/")[-1]
                    zf.writestr("БЛЯЯЯ/", "")
                    zf.writestr(f"БЛЯЯЯ/{filename_in_zip}", file_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка формирования архива: {e}"
            )

        zip_in_memory.seek(0)

        response = StreamingResponse(
            zip_in_memory,
            media_type="application/zip"
        )
        response.headers["Content-Disposition"] = "attachment; filename=archive.zip"
        return response
