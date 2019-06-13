from flask_wtf import FlaskForm
from wtforms import StringField, FileField,SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, input_required, url, Length

class CookieManager():
    def __init__(self, string):
        self.__cookie = string
    def get_cookie(self):
        return self.__cookie
    def setcookie(self, response):
        response.set_cookie("user", self.__cookie, path="/")
    def check(self, request):
        return request.cookie.get("user") == self.__cookie

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