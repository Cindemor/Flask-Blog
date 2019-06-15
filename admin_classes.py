from flask_wtf import FlaskForm
from wtforms import StringField, FileField,SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, input_required, url, Length


class SettingForm(FlaskForm):
    Sitename = StringField("sitename", validators=[DataRequired(message="该字段不可为空")])
    Logo = FileField("Logo")
    Sitedesc = StringField("sitedesc", validators=[DataRequired(message="该字段不可为空")])
    Sitegitloc = StringField("sitegitloc", validators=[url(message="请按url的格式输入")])
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

class aorpForm(FlaskForm):
    def __init__(self, name, status, date, author):
        self.__name = name
        self.__status = status
        self.__date = date
        self.__author = author
    def get_name(self):
        return self.__name
    def get_status(self):
        return self.__status
    def get_author(self):
        return self.__author
    def get_date(self):
        return self.__date

class aorpWriteForm(FlaskForm):
    Header = StringField("header", validators=[DataRequired(message="该字段不可为空")])
    Filename = StringField("filename", validators=[DataRequired(message="该字段不可为空")])
    Article = TextAreaField("article")