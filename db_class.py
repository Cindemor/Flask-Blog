class index_data():
    def __init__(self, s_title, pages, github, posts, year):
        self.__sitetitle = s_title #str
        self.__pages = pages # list
        self.__github = github #str
        self.__posts = posts #list
        self.__cpyear = year #str
    def get_attr(self, id):
        if id == 0:
            return self.__sitetitle
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.__github
        elif id == 3:
            return self.__posts
        elif id == 4:
            return self.__cpyear

class archives_data():
    def __init__(self, s_title, pages, github, mp, year):
        self.__sitetitle = s_title #str
        self.__pages = pages # list
        self.__github = github #str
        self.__mp = mp #list
        self.__cpyear = year #str
    def get_attr(self, id):
        if id == 0:
            return self.__sitetitle
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.__github
        elif id == 3:
            return self.__mp
        elif id == 4:
            return self.__cpyear

class aorp_data():
    def __init__(self, s_title, pages, github, title, date, info, ptitle, phref, ntitle, nhref, year, content):
        self.__sitetitle = s_title #str
        self.__pages = pages # list
        self.__github = github #str
        self.__title = title # str
        self.__date = date # str
        self.__info = info # str
        self.__ptitle = ptitle # str
        self.__phref = phref # str
        self.__ntitle = ntitle # str
        self.__nhref = nhref # str
        self.__cpyear = year #str
        self.__content = content #str
    def get_attr(self, id):
        if id == 0:
            return self.__sitetitle
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.__github
        elif id == 3:
            return self.__title
        elif id == 4:
            return self.__date
        elif id == 5:
            return self.__info
        elif id == 6:
            return self.__ptitle
        elif id == 7:
            return self.__phref
        elif id == 8:
            return self.__ntitle
        elif id == 9:
            return self.__nhref
        elif id == 10:
            return self.__cpyear
        elif id == 11:
            return self.__content