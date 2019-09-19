import environ

environ.Env.read_env('.env')

from .common import *

ALLOWED_HOSTS = ['localhost', '.ngrok.io', '134.209.170.40']
DEBUG = True
