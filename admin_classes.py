from flask_wtf import FlaskForm
from wtforms import StringField, FileField,SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, input_required, url, Length


class SettingForm(FlaskForm):
    Sitename = StringField("sitename", validators=[DataRequired()])
    Logo = FileField("Logo")
    Sitedesc = StringField("sitedesc")
    Sitegitloc = StringField("sitegitloc", validators=[DataRequired(message="不允许为空"), url(message="请按url的格式输入")])
    Sitebeian0 = StringField("sitebeian0")
    Sitebeian1 = StringField("sitebeian1")
    Siteloc = StringField("siteloc", validators=[url(message="请按url的格式输入")])
    Submit = SubmitField("submit_button")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(message="输入错误，请重新输入")])
    password= PasswordField("Password",validators=[
        DataRequired("密码不能为空"),
        Length(min=6, max=15, message="密码长度为6~15位字符")])
    check = BooleanField("remember-me-checkbox")
    submit=SubmitField("submit")

class IntroForm(FlaskForm):
    def __init__(self, sitename, articlenum, pagenum, articles):
        self.__sitename = sitename
        self.__articlenum = articlenum
        self.__pagenum = pagenum
        self.__articles = articles
    def get_sitename(self):
        return self.__sitename
    def get_articlenum(self):
        return self.__articlenum
    def get_pagenum(self):
        return self.__pagenum
    def get_articles(self):
        return self.__articles

class CookieCheck():
    def __init__(self, string1, string2):
        self.__string1 = string1
        self.__string2 = string2
    def check(self, request, session):
        return self.__string1 in request.cookies and self.__string2 in session
