import io
import zipfile
import minio
from fastapi import UploadFile, File, HTTPException, status, Query
from minio import S3Error
from starlette.responses import StreamingResponse

import config

minio_client = minio.Minio(
    access_key=config.MINIO_ACCESS_KEY,
    secret_key=config.MINIO_SECRET_KEY,
    secure=False,
    endpoint=config.MINIO_ENDPOINT
)


class StorageService:

    async def upload_file(self, file: UploadFile = File(...)):
        try:
            file_bytes = await file.read()
            file_size = len(file_bytes)

            data_stream = io.BytesIO(file_bytes)

            result = minio_client.put_object(
                config.MINIO_BUCKET,
                file.filename,
                data=data_stream,
                length=file_size,
                content_type=file.content_type
            )

            return {
                "message": "Файл успешно загружен",
                "filename": file.filename
            }
        except S3Error as err:
            raise HTTPException(status_code=500, detail=f"Ошибка при загрузке в MinIO: {err}")

    async def delete_file(self, filename: str):
        try:
            minio_client.remove_object(config.MINIO_BUCKET, filename)
            return {"message": f"Файл '{filename}' успешно удалён"}
        except S3Error as err:
            raise HTTPException(status_code=500, detail=f"Ошибка удаления файла: {err}")

    async def download_archive(
            self,
            keys: list[str] = Query(
                ...,
                description="Список ключей файлов, которые необходимо включить в архив"
            )
    ):
        zip_in_memory = io.BytesIO()

        try:
            with zipfile.ZipFile(zip_in_memory, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                folders = ["эксели/", "фотки/принятые/", "фотки/не принятые/"]
                for folder in folders:
                    zf.writestr(folder, "")

                for key in keys:
                    try:
                        response = minio_client.get_object(config.MINIO_BUCKET, key)
                        file_content = response["Body"].read()
                    except Exception as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Не удалось получить файл '{key}': {e}"
                        )
                    filename = key.split("/")[-1]

                    if filename.lower().endswith((".xls", ".xlsx")):
                        folder = "эксели/"
                    elif filename.lower().endswith((".jpg", ".jpeg", ".png")):
                        if "принят" in filename.lower():
                            folder = "фотки/принятые/"
                        else:
                            folder = "фотки/не принятые/"
                    else:
                        folder = ""

                    archive_path = f"{folder}{filename}"
                    zf.writestr(archive_path, file_content)
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


    async def get_link(self, name: str):
        try:
            download_url = minio_client.presigned_get_object(config.MINIO_BUCKET, name)
            return download_url
        except Exception:
            raise HTTPException(status_code=400)