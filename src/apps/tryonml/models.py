from src.utilities.base_model import BaseModel
from tortoise import fields
from tortoise.contrib.postgres.fields import ArrayField


class Usage(BaseModel):
    user = fields.ForeignKeyField(
        "models.User",
        related_name="usages",
        on_delete=fields.CASCADE,
        null=True
    )
    front_face = fields.ForeignKeyField(
        "models.File",
        related_name="front_face_usages",
        on_delete=fields.CASCADE,
        null=True
    )
    l_side_image = fields.ForeignKeyField(
        "models.File",
        related_name="l_side_usages",
        on_delete=fields.CASCADE,
        null=True
    )
    r_side_image = fields.ForeignKeyField(
        "models.File",
        related_name="r_side_usages",
        on_delete=fields.CASCADE,
        null=True
    )
    cloth_image = fields.ForeignKeyField(
        "models.File",
        related_name="cloth_usages",
        on_delete=fields.CASCADE,
        null=True
    )
    user_full_image = fields.ForeignKeyField(
        "models.File",
        related_name="full_image",
        on_delete=fields.CASCADE,
        null=True
    )
    output = fields.ForeignKeyField(
        "models.File",
        related_name="output_image",
        on_delete=fields.CASCADE,
        null=True
    )


    def __str__(self):
        return self.user.username
    

    class Meta:
        ordering = ['created_at', 'updated_at']
        table = "usage"
