# from pathlib import Path

# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent

# # Quick-start development settings - unsuitable for production
# SECRET_KEY = 'django-insecure-la4!63_j*3$k=6lk5f6#q4m0wwc6yo1@pxo-7rherf8u6ha^_q'

# DEBUG = True

# ALLOWED_HOSTS = []

# # Application definition
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'corsheaders',        # Включает пакет CORS безопасности
#     'rest_framework',     # Включает Django REST Framework
#     'rest_framework.authtoken',
#     'api',                # Подключает папку api с кодом
# ]

# # AUTH_USER_MODEL = 'api.User' # <-- Укажите имя вашего приложения вместо 'api', если оно другое

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',  # СТРОГО НА ПЕРВОМ МЕСТЕ (исправляет Network Error)
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'core.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'core.wsgi.application'

# # ТВОЯ НАСТОЯЩАЯ БАЗА ДАННЫХ POSTGRESQL (ИСПРАВЛЯЕТ ВЫЗОВ ФУНКЦИЙ):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'Delivery_food',       # <-- ЗАМЕНИ НА СВОЁ НАЗВАНИЕ БД
#         'USER': 'postgres',              # <-- СЮДА ВПИШИ ИМЯ ПОЛЬЗОВАТЕЛЯ (Обычно postgres)
#         'PASSWORD': '12345',        # <-- СЮДА ВПИШИ ПАРОЛЬ ОТ ТВОЕЙ БД POSTGRES
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }

# # НАСТРОЙКА КОРС-РАЗРЕШЕНИЙ (РАЗБЛОКИРУЕТ СВЯЗЬ С РЕАКТОМ):
# CORS_ALLOW_ALL_ORIGINS = True  
# CORS_ALLOW_CREDENTIALS = True

# НАСТРОЙКА КОРС-РАЗРЕШЕНИЙ:
# Указываем конкретный адрес вашего фронтенда (обязательно БЕЗ слэша на конце!)



# # Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# # Internationalization
# LANGUAGE_CODE = 'ru-ru'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# # Static files (CSS, JavaScript, Images)
# STATIC_URL = 'static/'

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # Настройки Django REST Framework
# # REST_FRAMEWORK = {
# #     'DEFAULT_AUTHENTICATION_CLASSES': [
# #         'rest_framework.authentication.SessionAuthentication',  # доступ для админки и браузера
# #         'rest_framework.authentication.TokenAuthentication',    # поддержка токенов для вашего React-фронтенда
# #     ],
# # }

# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend', # Проверяет админов в таблице auth_user
# ]

# # settings.py
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         # api.authentication.ClientTokenAuthentication', # Для клиентов на React
#         'api.authentication.CustomAuthtokenBackend', # Путь к созданному классу
#     ],
# }

# # REST_FRAMEWORK = {
# #     'DEFAULT_AUTHENTICATION_CLASSES': [
# #         'api.authentication.CustomAuthtokenBackend', # Путь к созданному классу
# #     ],
# # }



import os
from pathlib import Path
import dj_database_url  # Не забудьте добавить в requirements.txt!

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Чтение из переменных окружения Render. Если их нет (локально) — берутся дефолтные значения
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-la4!63_j*3$k=6lk5f6#q4m0wwc6yo1@pxo-7rherf8u6ha^_q')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Разрешаем локальный хост и все поддомены Render
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',        # Включает пакет CORS безопасности
    'rest_framework',     # Включает Django REST Framework
    'rest_framework.authtoken',
    'api',                # Подключает папку api с кодом
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # СТРОГО НА ПЕРВОМ МЕСТЕ (исправляет Network Error)
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Рекомендуется для раздачи статики (pip install whitenoise)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'


# БАЗА ДАННЫХ: Автопереключение между локальной и Render
if os.environ.get('DATABASE_URL'):
    # Настройки для Render (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # ТВОЯ ЛОКАЛЬНАЯ БАЗА ДАННЫХ POSTGRESQL (для разработки)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'Delivery_food',       
            'USER': 'postgres',            
            'PASSWORD': '12345',        
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }


# НАСТРОЙКА КОРС-РАЗРЕШЕНИЙ:
# Для безопасности в продакшене лучше указать конкретный адрес GitHub Pages вместо True
# CORS_ALLOW_ALL_ORIGINS = True  
# CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://univeraccsjs.github.io/web_delivery_frontend/",  # Замените на точный адрес вашей страницы GitHub Pages
]

CORS_ALLOW_CREDENTIALS = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Настройка для WhiteNoise (сжатие статики)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Настройка для WhiteNoise (сжатие и кэширование статики)
# STORAGES = {
#     "default": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Проверяет админов в таблице auth_user
]

# ИСПРАВЛЕНО: Объединили оба блока REST_FRAMEWORK в один, чтобы настройки не затирались
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',  # доступ для админки и браузера
        'rest_framework.authentication.TokenAuthentication',    # поддержка токенов для вашего React-фронтенда
        'api.authentication.CustomAuthtokenBackend',            # Ваш кастомный класс
    ],
}
