from .base_settings import *

INSTALLED_APPS.insert(INSTALLED_APPS.index('django.contrib.admin'), "slat_ldap")
AUTH_USER_MODEL = "slat_ldap.User"

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

