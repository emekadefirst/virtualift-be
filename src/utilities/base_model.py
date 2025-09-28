from tortoise import Model, fields, timezone

class BaseModel(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    updated_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]

    async def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = timezone.now()
        await super().save(*args, **kwargs)