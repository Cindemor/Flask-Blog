import os
from datetime import timedelta

class Config:
    DEBUG = True
    SECRET_KEY = "secret key"
    UPLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    REMEMBER_COOKIE_DURATION = timedelta(seconds=2)