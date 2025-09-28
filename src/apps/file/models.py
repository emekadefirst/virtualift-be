from tortoise import fields
from src.utilities.base_model import BaseModel
from src.enums.base import FileType


class File(BaseModel):
    name = fields.CharField(max_length=150)
    slug = fields.CharField(max_length=250, unique=True, index=True)
    type = fields.CharEnumField(FileType)
    extension = fields.CharField(max_length=10, null=True)
    mime_type = fields.CharField(max_length=100, null=True)
    url = fields.CharField(max_length=500) 
    size = fields.BigIntField() 
    width = fields.IntField(null=True) 
    height = fields.IntField(null=True)
    duration = fields.FloatField(null=True) 
    user = fields.ForeignKeyField("models.User", related_name="files", null=True)
    is_public = fields.BooleanField(default=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "files"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}.{self.extension} ({self.type})"
