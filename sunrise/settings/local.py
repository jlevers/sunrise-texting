import environ

environ.Env.read_env('.env')

from .common import *

ALLOWED_HOSTS = ['localhost', '06b4494f.ngrok.io']
