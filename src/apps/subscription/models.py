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
    user = fields.ForeignKeyField("models.User", related_name="user_subscription", null=True)
    duration = fields.CharEnumField(SubscriptionDuration)
    type = fields.CharEnumField(SubscriptionType)




class UsagePlan(BaseModel):
    usage_type = fields.CharEnumField(UsageType, unique=True) 
    max_usage = fields.IntField()
    monthly_cost = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    yearly_cost = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.usage_type} → {self.max_usage}"

    class Meta:
        table = "usage_plan"


class Usage(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="user_usage", null=True)
    ip_address = fields.CharField(max_length=45, null=True)
    usage_count = fields.IntField(default=0)
    max_usage = fields.IntField(default=0)
    usage_type = fields.CharEnumField(UsageType)
    is_subscribed = fields.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"{self.user.email} ({self.usage_type}) {self.usage_count}/{self.max_usage}"
        return f"{self.ip_address} ({self.usage_type}) {self.usage_count}/{self.max_usage}"

    class Meta:
        table = "usage"
