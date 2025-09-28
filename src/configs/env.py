import os
from dotenv import load_dotenv

load_dotenv()


CLOUDINARY_CLOUD_NAME = str(os.getenv('CLOUDINARY_CLOUD_NAME'))
CLOUDINARY_API_KEY = str(os.getenv('CLOUDINARY_API_KEY'))
CLOUDINARY_API_SECRET = str(os.getenv('CLOUDINARY_API_SECRET'))
CLOUDINARY_URL = str(os.getenv('CLOUDINARY_URL'))

DB_NAME = str(os.getenv('DB_NAME'))
DB_HOST = str(os.getenv('DB_HOST'))
DB_PASSWORD = str(os.getenv('DB_PASSWORD'))
DB_PORT = str(os.getenv('DB_PORT'))
DB_USER = str(os.getenv('DB_USER'))

TEST_DATABASE_URL = str(os.getenv('TEST_DATABASE_URL'))

JWT_ACCESS_EXPIRY = int(os.getenv('JWT_ACCESS_EXPIRY'))
JWT_REFRESH_EXPIRY = int(os.getenv('JWT_REFRESH_EXPIRY'))
JWT_ACCESS_SECRET = str(os.getenv('JWT_ACCESS_SECRET'))
JWT_REFRESH_SECRET = str(os.getenv('JWT_REFRESH_SECRET'))
JWT_ALGORITHM = str(os.getenv('JWT_ALGORITHM'))

HF_TOKEN = str(os.getenv("HF_TOKEN") )