from src.utilities.base_model import BaseModel
from tortoise import fields
from src.enums.base import PaymentStatus
from src.utilities.id_generators import payment_id


class Payment(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="user_payment")
    subscription = fields.ForeignKeyField("models.Subscription", related_name="user_subscription")
    payment_time = fields.DatetimeField()
    status = fields.CharEnumField(PaymentStatus)
    reciept_id = fields.CharField(null=True, default=payment_id, unique=True)
    amount = fields.DecimalField()