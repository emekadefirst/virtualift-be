from src.configs.env import (
    DB_HOST,
    DB_NAME,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    TEST_DATABASE_URL,
)
from tortoise import Tortoise
from urllib.parse import quote_plus




TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": DB_HOST,
                "port": DB_PORT,
                "user": DB_USER,
                "password": DB_PASSWORD,
                "database": DB_NAME
            },
        }
    },
    "apps": {
        "models": {
            "models": ["src.core.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}



TEST_TORTOISE_ORM = {
    "connections": {"models": TEST_DATABASE_URL},
    "apps": {
        "models": {
            "models": ["src.core.models"],
            "default_connection": "models",
        }
    },
    "use_tz": False,
    "timezone": "UTC",
}