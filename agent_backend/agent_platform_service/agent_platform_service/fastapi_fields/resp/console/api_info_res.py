# schemas.py
from typing import Optional

from pydantic import BaseModel


class ApiInfoExportedResp(BaseModel):
    data: Optional[str] = None


class ApiInfoImportResp(BaseModel):
    data: Optional[str] = None


class ApiInfoInsertResp(BaseModel):
    data: Optional[str] = None


class ApiInfoUpdateResp(BaseModel):
    data: Optional[str] = None


class ApiInfoDeleteResp(BaseModel):
    data: Optional[str] = None
