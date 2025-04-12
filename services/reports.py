import http

import pandas as pd
from fastapi import UploadFile, HTTPException
from io import BytesIO
from typing import List
from utils.unitofwork import IUnitOfWork


class ReportService:
    async def get_report(self, uow: IUnitOfWork, _id: int):
        return await uow.reports.find_one(id=_id)

    async def delete_report(self, uow: IUnitOfWork, _id: int):
        report_id = await uow.reports.delete_one(_id)
        await uow.commit()
        return report_id

    @staticmethod
    async def post_report(files: List[UploadFile]):
        merged_df = pd.DataFrame()

        for file in files:
            if not file.filename.endswith((".xls", ".xlsx")):
                continue

            try:
                content = await file.read()
                df = pd.read_excel(BytesIO(content), engine="openpyxl")
                merged_df = pd.concat([merged_df, df], ignore_index=True)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ошибка при чтении {file.filename}: {str(e)}"
                )

        return http.HTTPStatus.OK