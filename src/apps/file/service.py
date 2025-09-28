import os
import mimetypes
from fastapi import UploadFile
from typing import List, Optional
from src.error.base import ErrorHandler
from src.apps.file.models import File
from src.libs.cloudinary import ObjectStService
from src.utilities.base_service import BaseModelService


class FileService:
    boa = BaseModelService(File)
    model = File
    bucket = ObjectStService
    error = ErrorHandler(File)

    @classmethod
    async def save(cls, **kwargs) -> File:
        return await cls.model.create(**kwargs)

    @classmethod
    async def upload(cls, file: Optional[UploadFile], user_id: Optional[str] = None) -> List[File]:

        url = await cls.bucket.upload(file)
        filename, ext = os.path.splitext(file.filename)
        ext = ext.replace(".", "").lower()
        mime_type = mimetypes.guess_type(file.filename)[0]
        file_data = {
            "name": filename,
            "slug": filename.replace(" ", "_").lower(),
            "extension": ext,
            "mime_type": mime_type,
            "url": url,
            "size": file.size,
            "user_id": user_id,
            "type": cls._get_file_type(ext),
        }
        
        saved_file = await cls.model.create(**dict(file_data))
        return saved_file

    @staticmethod
    def _get_file_type(ext: str) -> str:
        from src.enums.base import ImageExtension, VideoExtension, DocumentExtension, AudioExtension, FileType

        if ext in ImageExtension._value2member_map_:
            return FileType.IMAGE
        if ext in VideoExtension._value2member_map_:
            return FileType.VIDEO
        if ext in DocumentExtension._value2member_map_:
            return FileType.DOCUMENT
        if ext in AudioExtension._value2member_map_:
            return FileType.AUDIO
        return FileType.DOCUMENT  
