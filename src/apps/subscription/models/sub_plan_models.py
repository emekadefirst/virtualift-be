from tortoise import fields
from src.utilities.base_model import BaseModel
from src.enums.base import UsageType, SubscriptionType, SubscriptionDuration

class SubscriptionPlan(BaseModel):
    name = fields.CharField(max_length=100, unique=True)  
    type = fields.CharEnumField(SubscriptionType)
    duration = fields.CharEnumField(SubscriptionDuration)
    max_usage = fields.IntField(default=0)
    cost = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.type}, {self.duration})"

    class Meta:
        table = "subscription_plan"
        unique_together = ("type", "duration")
        

class Subscription(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="subscriptions")
    plan = fields.ForeignKeyField("models.SubscriptionPlan", related_name="subscriptions")
    start_date = fields.DatetimeField(auto_now_add=True)
    end_date = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} → {self.plan.name} ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        table = "subscription"
        ordering = ["-start_date"]
