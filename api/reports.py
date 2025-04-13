from fastapi import APIRouter, UploadFile, File, Query

import config
from api.dependencies import UOWDep
from services.reports import ReportService
from services.storage import StorageService
from utils.unitofwork import IUnitOfWork

router = APIRouter(prefix="/report", tags=["Reports"])


@router.get("/")
async def get_report(
        report_id: int
):
    return await ReportService().get_report(report_id)


@router.get("/all")
async def get_all_reports(
        uow: UOWDep):
    return await ReportService().get_all(uow)


@router.post("")
async def post_report(files: list[UploadFile] = File(...)):
    return await ReportService().post_report(files)


@router.get("zip")
async def get_zip(keys: list[str] = Query(
    ...,
    description="Список ключей файлов, которые необходимо включить в архив"
)):
    return await StorageService().download_archive(keys)


