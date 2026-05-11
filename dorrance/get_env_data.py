import os
import ast
from dotenv import load_dotenv
load_dotenv()


Debug = os.getenv('DEBUG') in ['true', '1', 'yes', 'True']

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

TIMEZONE = os.getenv('TIMEZONE', 'Asia/Kolkata')
CELERY_HOUR = int(os.getenv('CELERY_HOUR', 8))
CELERY_MINUTE = int(os.getenv('CELERY_MINUTE', 30))




Allowed_origin = os.getenv('ALLOWED_ORIGIN')
ALLOWED_ORIGIN = ast.literal_eval(Allowed_origin) if Allowed_origin else ['http://127.0.0.1:8000']
ALLOWED_DOMAIN = str(os.getenv('DOMAIN')).strip().split(',')
CSRF_ORIGINS = str(os.getenv('CSRF_ORIGINS')).strip().split(',')
BASE_URL = str(os.getenv('BASE_URL'))

USE_REDIS = True if os.getenv('USE_REDIS', False) and os.getenv('USE_REDIS', False) == 'True' else False

WHATSAPP_ACCOUNT_SID = os.getenv('WHATSAPP_ACCOUNT_SID')
WHATSAPP_AUTH_TOKEN = os.getenv('WHATSAPP_AUTH_TOKEN')
WHATSAPP_FROM_MOBILE = os.getenv('WHATSAPP_FROM_MOBILE')
WHATSAPP_STATUS_CALLBACK_URL = os.getenv('WHATSAPP_STATUS_CALLBACK_URL', None)


COUNTRY_CODE = os.getenv('COUNTRY_CODE')

CAS_DOMAIN = os.getenv('CAS_DOMAIN')

AWS_DATA = {
    'AWS_ACCESS_KEY_ID':os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY':os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_S3_REGION_NAME':os.getenv('AWS_S3_REGION_NAME'),
    'AWS_STORAGE_BUCKET_NAME':os.getenv('AWS_STORAGE_BUCKET_NAME'),
    'AWS_S3_CUSTOM_DOMAIN':os.getenv('AWS_S3_CUSTOM_DOMAIN'),
    'GMB_AWS_S3_URL':os.getenv('GMB_AWS_S3_URL'),
    'GMB_AWS_S3_URL_STATIC':os.getenv('GMB_AWS_S3_URL_STATIC'),
}

MAIL_HOST = os.getenv('MAIL_HOST')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_ENCRYPTION_SSL = os.getenv('MAIL_ENCRYPTION_SSL') in ['true', '1', 'yes', 'True']
