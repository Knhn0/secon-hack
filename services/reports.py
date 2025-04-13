import http

import pandas as pd
from fastapi import UploadFile, HTTPException, status
from io import BytesIO
from typing import List

from services.ai import AIService
from services.storage import StorageService
from utils.unitofwork import IUnitOfWork


class ReportService:
    async def get_report(self, uow: IUnitOfWork, _id: int):
        return await uow.reports.find_one(id=_id)

    async def delete_report(self, uow: IUnitOfWork, _id: int):
        report_id = await uow.reports.delete_one(_id)
        await uow.commit()
        return report_id

    async def get_all(self, uow: IUnitOfWork):
        return await uow.reports.find_all()

    async def post_report(files: List[UploadFile]):
        merged_df = pd.DataFrame()

        for file in files:
            if not file.filename.endswith((".xls", ".xlsx")):
                continue
            recognized_text = await AIService().handle_file(file)
            if recognized_text == "Номер не найден":
                file.filename = "Unrecognized_Number"
            else:
                ...
            await StorageService().upload_file(file)

            try:
                content = await file.read()
                if file.filename.endswith('.xlsx'):
                    df = pd.read_excel(BytesIO(content), engine="openpyxl")
                else:
                    df = pd.read_excel(BytesIO(content), engine="xlrd")
                merged_df = pd.concat([merged_df, df], ignore_index=True)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка при чтении {file.filename}: {str(e)}"
                )

        return http.HTTPStatus.OK
