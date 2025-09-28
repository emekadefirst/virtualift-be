import uuid
import random
import string


def subscription_id() -> str:
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"sub_{rand}_{uuid.uuid4().hex[:8]}"


def payment_id() -> str:
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"pay_{rand}"
