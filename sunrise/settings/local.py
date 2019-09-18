import environ

environ.Env.read_env('.env')

from .common import *

ALLOWED_HOSTS = ['localhost', 'a64398df.ngrok.io']
