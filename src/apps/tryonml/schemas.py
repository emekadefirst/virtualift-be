from pydantic import BaseModel
from typing import Optional


class FileUploadSchema(BaseModel):
    id: Optional[str] = None
    image_url: Optional[str] = None


class DataSchema(BaseModel):
    product_image: Optional[FileUploadSchema] = None
    front_image: Optional[FileUploadSchema] = None
    l_image: Optional[FileUploadSchema] = None
    r_image: Optional[FileUploadSchema] = None
    user_full_image: Optional[FileUploadSchema] = None
    product_image_url: Optional[str] = None