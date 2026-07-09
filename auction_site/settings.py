import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-secret")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
##############
ALLOWED_HOSTS = ['*']
LOGIN_URL = 'login'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

AUTH_USER_MODEL = 'auctions.User' # Thay 'myapp' bằng tên app của bạn

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db' # Kết hợp DB và Cache
SESSION_COOKIE_AGE = 1209600 # 2 tuần (tùy chỉnh theo yêu cầu)
SESSION_SAVE_EVERY_REQUEST = True # Đảm bảo session được cập nhật liên tục

##############
# Application definition

INSTALLED_APPS = [
    'channels',
    'auctions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

ASGI_APPLICATION = 'auction_site.asgi.application'

# Cấu hình CHANNEL_LAYERS tối ưu cho Upstash Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": os.getenv("REDIS_URL"),
                    "health_check_interval": 15,  # Gửi PING mỗi 15 giây để giữ kết nối
                    "socket_keepalive": True,     # Bật TCP keepalive
                    "retry_on_timeout": True,     # Tự động kết nối lại khi bị timeout
                }
            ],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Đường dẫn tới thư mục chứa các file tĩnh khi đã gom lại (collectstatic)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Quan trọng: Cấu hình để Whitenoise phục vụ file tĩnh
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'auction_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'auction_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True  # Quan trọng: Render yêu cầu kết nối SSL
        )
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

# 1. Đặt múi giờ hiển thị mặc định là Việt Nam
TIME_ZONE = 'Asia/Ho_Chi_Minh'

# 2. BẮT BUỘC để True: Django sẽ lưu vào DB dưới dạng UTC 
# nhưng khi lấy ra sẽ tự chuyển về Asia/Ho_Chi_Minh cho bạn
USE_TZ = True 

# 3. Đảm bảo ngôn ngữ hiển thị đúng định dạng Việt Nam
LANGUAGE_CODE = 'vi'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = BASE_DIR / "staticfiles"

CSRF_TRUSTED_ORIGINS = [
    'https://auction-web-django-4.onrender.com',
    'https://*.onrender.com', # Cho phép tất cả các subdomain của render nếu cần
]

# Cấu hình Email gửi đi
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Khai báo Email mặc định gửi đi (lấy từ môi trường hoặc giá trị mặc định)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
EMAIL_TIMEOUT = 10