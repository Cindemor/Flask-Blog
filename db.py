from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Siteclass():
    __sitename = str()

    def __init__(self, string):
        self.__sitename = string

    def get_sitename(self):
        return self.__sitename