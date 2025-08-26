# Django settings for myshop project.
from pathlib import Path
import os
from dotenv import load_dotenv  # Import the load_dotenv function from dotenv
import dj_database_url  # Import the dj_database_url module

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = "/media/"  # URL de base pour les fichiers médias
MEDIA_ROOT = os.path.join(
    BASE_DIR, "media"
)  # Chemin absolu vers le dossier des fichiers médias


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-#o!3w)%#7(etx0@ylh_7fou9z5hzweq@5*zp!g^#6(ch!#@1m_"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "api",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # Si vous avez d'autres classes d'authentification (ex: SessionAuthentication)
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",  # C'est une bonne valeur par défaut pour les API JWT
    ),
    # ... autres configurations DRF si vous en avez
}

from datetime import timedelta  # N'oubliez pas d'importer timedelta !

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        hours=8
    ),  # Le token d'accès sera valide 8 heures
    "REFRESH_TOKEN_LIFETIME": timedelta(
        weeks=2
    ),  # Le token de rafraîchissement sera valide 2 semaines
    # --- Paramètres de sécurité et de rotation des tokens (hautement recommandés) ---
    "ROTATE_REFRESH_TOKENS": True,  # Quand un refresh token est utilisé, un nouveau est généré
    "BLACKLIST_AFTER_ROTATION": True,  # L'ancien refresh token est blacklisté après rotation
    "UPDATE_LAST_LOGIN": False,  # Optionnel: met à jour le champ last_login de l'utilisateur
    # --- Autres paramètres par défaut (généralement pas besoin de les modifier) ---
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # Utilise votre SECRET_KEY de Django
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_USER_MODEL": "api.User",
    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),  # Le type de préfixe pour le token dans l'en-tête Authorization
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    # Pour les tokens "glissants" (Sliding Tokens), si vous les utilisiez. Pas nécessaires pour votre cas.
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

CORS_ALLOW_ALL_ORIGINS = True
AUTH_USER_MODEL = "api.User"
FRONTEND_BASE_URL = "http://localhost:5173/"
ROOT_URLCONF = "myshop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "myshop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# Détecter l'environnement (local ou production)
# ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # Par défaut, 'development'

# if ENVIRONMENT == "production":
#     # Configuration pour PostgreSQL en production
#     DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}
# else:
#     # Configuration pour SQLite en développement local
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#         }
#     }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "my_shop_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "francelKazakh*2022"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuration de l'envoi d'e-mails
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Utilisez le serveur SMTP de votre fournisseur d'e-mails
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")  # Remplacez par votre adresse e-mail
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD"
)  # Remplacez par votre mot de passe ou un mot de passe d'application
