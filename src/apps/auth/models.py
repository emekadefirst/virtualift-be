from src.utilities.base_model import BaseModel
from tortoise import fields
from src.enums.base import Action, Resource
from src.utilities.crypto import set_password


class Permission(BaseModel):
    resource = fields.CharEnumField(Resource)
    action = fields.CharEnumField(Action)

    class Meta:
        table = "permissions"

class PermissionGroup(BaseModel):
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    permissions = fields.ManyToManyField(
        "models.Permission",
        related_name="permission_groups",
        through="permission_group_permissions",
    )

    class Meta:
        table = "permission_groups"


class User(BaseModel):
    first_name = fields.CharField(50, null=True)
    last_name = fields.CharField(50, null=True)
    email = fields.CharField(200, unique=True)
    username = fields.CharField(200, null=True, unique=True)
    app_name = fields.CharField(200, unique=True, null=True)
    password = fields.CharField(200)
    is_verified = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)
    ip_address = fields.CharField(max_length=45, null=True)
    permission_groups = fields.ManyToManyField("models.PermissionGroup")

    def __str__(self):
        return self.email

    class Meta:
        table = "users"

    async def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("$argon2"):
            self.password = set_password(self.password)
        await super().save(*args, **kwargs)