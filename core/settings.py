import os
import random
import string
from pathlib import Path
from dotenv import load_dotenv
from str2bool import str2bool

# Este es un comentario para forzar un nuevo commit

load_dotenv()  # Cargar variables de entorno desde .env

# Construir rutas dentro del proyecto como BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # Corregido aquí

# Configuración de seguridad
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

# Modo de depuración
DEBUG = True

ALLOWED_HOSTS = ['*']

# Añadir tus hosts de despliegue aquí
CSRF_TRUSTED_ORIGINS = [
    'https://weeegoapp-btgcf0eccmh0a4h9.eastus-01.azurewebsites.net',
    'http://localhost:8000',
    'http://localhost:5085',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:5085',
]

render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f'https://{render_hostname}')
# Configuración de aplicaciones
INSTALLED_APPS = [
    'admin_berry.apps.AdminBerryConfig',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "home",
]

# Configuración de middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Configuración de URLs
ROOT_URLCONF = "core.urls"

HOME_TEMPLATES = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Configuración de base de datos
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'RECOLECCION_BD',  # Nombre de tu base de datos
        'USER': 'admin1',  # Usuario de Azure SQL
        'PASSWORD': 'Weeego123',  # Contraseña de Azure SQL
        'HOST': 'srvweeegoo.database.windows.net',  # Servidor de Azure SQL
        'PORT': '1433',  # Puerto de Azure SQL (por defecto 1433)
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes',
        },
    }
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internacionalización
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_MANIFEST_STRICT = False

# Configuración de almacenamiento de archivos estáticos
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración de campo clave primaria
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuración de redirección de login
LOGIN_REDIRECT_URL = '/'

# Configuración de backend de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'