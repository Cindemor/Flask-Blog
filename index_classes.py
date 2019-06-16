class base_data():
    def __init__(self, s_title, github, year, picurl):
        self.__sitetitle = s_title
        self.__github = github
        self.__year = year
        self.__picurl = picurl
    def get_year(self):
        return self.__year
    def get_github(self):
        return self.__github
    def get_sitetitle(self):
        return self.__sitetitle
    def get_picurl(self):
        return self.__picurl

class index_data(base_data):
    def __init__(self, s_title, pages, github, posts, year, picurl):
        super(index_data, self).__init__(s_title, github, year, picurl)
        self.__pages = pages # list
        self.__posts = posts #list
    def get_attr(self, id):
        if id == 0:
            return self.get_sitetitle()
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.get_github()
        elif id == 3:
            return self.__posts
        elif id == 4:
            return self.get_year()
        elif id == 5:
            return self.get_picurl()

class archives_data(base_data):
    def __init__(self, s_title, pages, github, mp, year, picurl):
        super(archives_data, self).__init__(s_title, github, year, picurl)
        self.__pages = pages # list
        self.__mp = mp #list
    def get_attr(self, id):
        if id == 0:
            return self.get_sitetitle()
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.get_github()
        elif id == 3:
            return self.__mp
        elif id == 4:
            return self.get_year()
        elif id == 5:
            return self.get_picurl()

class aorp_data(base_data):
    def __init__(self, s_title, pages, github, title, date, info, ptitle, phref, ntitle, nhref, year, content, picurl):
        super(aorp_data, self).__init__(s_title, github, year, picurl)
        self.__pages = pages # list
        self.__title = title # str
        self.__date = date # str
        self.__info = info # str
        self.__ptitle = ptitle # str
        self.__phref = phref # str
        self.__ntitle = ntitle # str
        self.__nhref = nhref # str
        self.__content = content #str
    def get_attr(self, id):
        if id == 0:
            return self.get_sitetitle()
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.get_github()
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
            return self.get_year()
        elif id == 11:
            return self.__content
        elif id == 12:
            return self.get_picurl()