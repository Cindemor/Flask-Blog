import os
from datetime import timedelta

class Config:
    DEBUG = True
    SECRET_KEY = "secret key"
    UPLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    #SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)