"""
Django settings for double_codification project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
from decouple import config
import ldap
from django_auth_ldap.config import LDAPSearch, LDAPSearchUnion, NestedActiveDirectoryGroupType
from django_auth_ldap.backend import populate_user
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = [
    "srvdocker",
    "localhost",
    "127.0.0.1",
    "10.21.92.109",
    'testserver',
]
LOGIN_REDIRECT_URL = 'selectouvrage'
LOGOUT_REDIRECT_URL = 'index'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )

}
# Application definition

SHARED_APPS = (
    'django_tenants',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'corsheaders',
    'rest_framework',
    'django_tables2',
    'rest_framework_simplejwt',
    "crispy_forms",
    "crispy_tailwind",
    "drf_yasg",
)
TENANT_APPS =(
    'core',
)
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]
MIDDLEWARE = [    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',    
    # 'django_tenants.middleware.main.TenantMainMiddleware',
]

ROOT_URLCONF = 'double_codification.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'double_codification.wsgi.application'
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
# }

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs/doublecodif.log'),
#             'formatter': 'verbose',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file', 'console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'core': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     },
# }


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME', default='v1'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='123456'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),

    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = '/static/'
# STATIC_ROOT = '/static/'
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static/'
# CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
# CRISPY_TEMPLATE_PACK = "tailwind"
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOWED_ORIGINS = ["http://loaclhost:8000","http://srvdocker:5856"]
CSRF_TRUSTED_ORIGINS = [
    "http://srvdocker:5856",
    "http://localhost:8000",
    "http://10.21.92.109",
]
# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_METHODS = [
#     'GET',
#     'POST',
#     # 'PUT',
#     # 'PATCH',
#     # 'DELETE',
#     # 'OPTIONS',
# ]

# CORS_ALLOW_HEADERS = [
#     'content-type',
#     'authorization',
#     'x-csrftoken',
# ]

# CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TENANT_MODEL = "core.Ouvrage"




# AD
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]

"""
svc-dblcod 
+G#WCGa537  
"""
AUTH_LDAP_SERVER_URI = "LDAP://a0-dcdns01.casn.net"
AUTH_LDAP_BIND_DN = "CN=svc-dblcod,OU=Techniques,OU=Utilisateurs_Non_Personnel,OU=AYFr,DC=casn,DC=net"
AUTH_LDAP_BIND_PASSWORD = "+G#WCGa537"


def is_user_active(ldap_user):
    """ Vérifie si l'utilisateur appartient à un des groupes LDAP autorisés """
    active_groups = {
        "CN=DC_SUPPORT,OU=Groupes Manuels ACE,OU=Groupes,OU=AYFr,DC=casn,DC=net",
        "CN=DC_J35_VIEWER,OU=Groupes Manuels ACE,OU=Groupes,OU=AYFr,DC=casn,DC=net",
        "CN=DC_J35_EDITOR,OU=Groupes Manuels ACE,OU=Groupes,OU=AYFr,DC=casn,DC=net",
    }

   
    if any(group in (ldap_user.group_dns or []) for group in active_groups):
        return True   
    return is_user_superuser(ldap_user) 

def is_user_superuser(ldap_user):  
    superuser_groups = {
        "CN=DC_J35_VIEWER,OU=Groupes Manuels ACE,OU=Groupes,OU=AYFr,DC=casn,DC=net"
    }

    return any(group in (ldap_user.group_dns or []) for group in superuser_groups)

populate_user.connect(lambda user, ldap_user: setattr(user, "is_active", is_user_active(ldap_user)))
populate_user.connect(lambda user, ldap_user: setattr(user, "is_superuser", is_user_superuser(ldap_user)))


AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

AUTH_LDAP_CONNECTION_OPTIONS = { ldap.OPT_REFERRALS: 0 }

AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch("OU=Utilisateurs,OU=AYFr,DC=casn,DC=net", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)"),
    LDAPSearch("OU=Utilisateurs_Non_Personnel,OU=AYFr,DC=casn,DC=net", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")
)

AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_MIRROR_GROUPS = True
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "OU=Groupes,OU=AYFr,DC=casn,DC=net", 
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)",
)

AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_USER_FLAGS_BY_GROUP = {}
AUTH_LDAP_USER_FLAGS_BY_FUNC = {
    "is_active": is_user_active,
    "is_superuser": is_user_superuser,
}

import logging
logger = logging.getLogger("django_auth_ldap")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


