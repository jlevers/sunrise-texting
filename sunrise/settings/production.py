import environ

environ.Env.read_env('.env')

from .common import *

DEBUG = False
ALLOWED_HOSTS = ['134.209.170.40', 'localhost', '.twilio.com']
