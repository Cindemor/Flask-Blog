from flask_wtf import FlaskForm
from wtforms import StringField, FileField,SubmitField
from wtforms.validators import DataRequired, input_required, url

class Template(FlaskForm):
    Sitename = StringField("sitename", validators=[DataRequired()])
    Logo = FileField("Logo")
    Sitedesc = StringField("sitedesc")
    Sitegitloc = StringField("sitegitloc", validators=[DataRequired(message="不允许为空"), url(message="请按url的格式输入")])
    Sitebeian0 = StringField("sitebeian0")
    Sitebeian1 = StringField("sitebeian1")
    Siteloc = StringField("siteloc", validators=[url(message="请按url的格式输入")])
    Submit = SubmitField("submit_button")
