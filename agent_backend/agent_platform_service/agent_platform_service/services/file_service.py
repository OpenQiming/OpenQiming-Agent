import datetime
import hashlib
import uuid
from typing import Any, Literal, Union

from flask_login import current_user
from werkzeug.exceptions import NotFound

from agent_platform_common.configs import agent_platform_config
from agent_platform_common.constants import (
    AUDIO_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
)
from agent_platform_core.contexts import tenant_id
from agent_platform_core.file import helpers as file_helpers
from agent_platform_core.rag.extractor.extract_processor import ExtractProcessor
from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.extensions.ext_storage import storage
from agent_platform_basic.models.db_model.account import Account
from agent_platform_core.models.enum_model.enums import CreatedByRole
from agent_platform_core.models.db_model.model import EndUser, UploadFile, App

from agent_platform_basic.exceptions.services.file import FileTooLargeError, UnsupportedFileTypeError

PREVIEW_WORDS_LIMIT = 3000


class FileService:
    @staticmethod
    def upload_file(
        *,
        filename: str,
        content: bytes,
        tenant_id: str = "",
        mimetype: str,
        user: Union[Account, EndUser, Any],
        source: Literal["datasets"] | None = None,
        source_url: str = "",
        app_id: str = "",
    ) -> UploadFile:
        # get file extension
        extension = filename.split(".")[-1].lower()
        if len(filename) > 200:
            filename = filename.split(".")[0][:200] + "." + extension

        if source == "datasets" and extension not in DOCUMENT_EXTENSIONS:
            raise UnsupportedFileTypeError()

        if extension not in DOCUMENT_EXTENSIONS:
            raise UnsupportedFileTypeError()

        # get file size
        file_size = len(content)

        # check if the file size is exceeded
        if not FileService.is_file_size_within_limit(extension=extension, file_size=file_size):
            raise FileTooLargeError

        # generate file key
        file_uuid = str(uuid.uuid4())

        if isinstance(user, Account):
            current_tenant_id = tenant_id or user.current_tenant_id
        elif user is None: #省测调用 不用token 所有没有用户信息
            x = db.session.query(App.tenant_id).where(App.id==app_id).first()
            current_tenant_id = x.tenant_id
        else:
            # end_user
            current_tenant_id = user.tenant_id

        file_key = "upload_files/" + current_tenant_id + "/" + file_uuid + "." + extension

        # save file to storage
        storage.save(file_key, content)

        # save file to db
        upload_file = UploadFile(
            tenant_id=current_tenant_id,
            storage_type=agent_platform_config.STORAGE_TYPE,
            key=file_key,
            name=filename,
            size=file_size,
            extension=extension,
            mime_type=mimetype,
            created_by_role=(CreatedByRole.ACCOUNT if isinstance(user, Account) else CreatedByRole.END_USER),
            created_by=user.id if user else str(uuid.uuid4()), #没有用户信息只能随便写一个
            created_at=datetime.datetime.now().replace(tzinfo=None),
            used=False,
            hash=hashlib.sha3_256(content).hexdigest(),
            source_url=source_url,
        )

        db.session.add(upload_file)
        db.session.commit()

        return upload_file

    @staticmethod
    def is_file_size_within_limit(*, extension: str, file_size: int) -> bool:
        if extension in IMAGE_EXTENSIONS:
            raise UnsupportedFileTypeError()
            # file_size_limit = agent_platform_config.UPLOAD_IMAGE_FILE_SIZE_LIMIT * 1024 * 1024
        elif extension in VIDEO_EXTENSIONS:
            raise UnsupportedFileTypeError()
            # file_size_limit = agent_platform_config.UPLOAD_VIDEO_FILE_SIZE_LIMIT * 1024 * 1024
        elif extension in AUDIO_EXTENSIONS:
            raise UnsupportedFileTypeError()
            # file_size_limit = agent_platform_config.UPLOAD_AUDIO_FILE_SIZE_LIMIT * 1024 * 1024
        else:
            file_size_limit = agent_platform_config.UPLOAD_FILE_SIZE_LIMIT * 1024 * 1024

        return file_size <= file_size_limit

    @staticmethod
    def upload_text(text: str, text_name: str) -> UploadFile:
        if len(text_name) > 200:
            text_name = text_name[:200]
        # user uuid as file name
        file_uuid = str(uuid.uuid4())
        file_key = "upload_files/" + current_user.current_tenant_id + "/" + file_uuid + ".txt"

        # save file to storage
        storage.save(file_key, text.encode("utf-8"))

        # save file to db
        upload_file = UploadFile(
            tenant_id=current_user.current_tenant_id,
            storage_type=agent_platform_config.STORAGE_TYPE,
            key=file_key,
            name=text_name,
            size=len(text),
            extension="txt",
            mime_type="text/plain",
            created_by=current_user.id,
            created_by_role=CreatedByRole.ACCOUNT,
            created_at=datetime.datetime.now().replace(tzinfo=None),
            used=True,
            used_by=current_user.id,
            used_at=datetime.datetime.now().replace(tzinfo=None),
        )

        db.session.add(upload_file)
        db.session.commit()

        return upload_file

    @staticmethod
    def get_file_preview(file_id: str):
        upload_file = db.session.query(UploadFile).filter(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found")

        # extract text from file
        extension = upload_file.extension
        if extension.lower() not in DOCUMENT_EXTENSIONS:
            raise UnsupportedFileTypeError()

        text = ExtractProcessor.load_from_upload_file(upload_file, return_text=True)
        text = text[0:PREVIEW_WORDS_LIMIT] if text else ""

        return text

    @staticmethod
    def get_image_preview(file_id: str, timestamp: str, nonce: str, sign: str):
        result = file_helpers.verify_image_signature(
            upload_file_id=file_id, timestamp=timestamp, nonce=nonce, sign=sign
        )
        if not result:
            raise NotFound("File not found or signature is invalid")

        upload_file = db.session.query(UploadFile).filter(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found or signature is invalid")

        # extract text from file
        extension = upload_file.extension
        if extension.lower() not in IMAGE_EXTENSIONS:
            raise UnsupportedFileTypeError()

        generator = storage.load(upload_file.key, stream=True)

        return generator, upload_file.mime_type

    @staticmethod
    def get_file_generator_by_file_id(file_id: str, timestamp: str, nonce: str, sign: str):
        result = file_helpers.verify_file_signature(upload_file_id=file_id, timestamp=timestamp, nonce=nonce, sign=sign)
        if not result:
            raise NotFound("File not found or signature is invalid")

        upload_file = db.session.query(UploadFile).filter(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found or signature is invalid")

        generator = storage.load(upload_file.key, stream=True)

        return generator, upload_file

    @staticmethod
    def get_public_image_preview(file_id: str):
        upload_file = db.session.query(UploadFile).filter(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found or signature is invalid")

        # extract text from file
        extension = upload_file.extension
        if extension.lower() not in IMAGE_EXTENSIONS:
            raise UnsupportedFileTypeError()

        generator = storage.load(upload_file.key)

        return generator, upload_file.mime_type
