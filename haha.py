from config import Config
from templates_class import Template
from flask import Flask, render_template, redirect, request, session, flash, send_from_directory, Session
from flask_wtf.file import  FileStorage
import os
from db import db, Siteclass
from DBObj import DBObject
from sqlalchemy.schema import CreateTable

app = Flask(__name__)
app.config.from_object(Config)
app.debug = True
db.init_app(app)


@app.route("/", methods=["GET"])
def jump():
    return redirect("index")

@app.route("/index", methods=["GET", "POST"])
def index_page():
    print(request.query_string)
    db.create_all()
    form = Template()
    # print(DBObject.query.all())
    # print(DBObject.query.order_by(DBObject.sitename.desc()).all())
    # print(DBObject.query.filter(DBObject.sitename.like('spidere%')).all())
    # print(DBObject.query.get(2).sitename)
    # if "Logoname" not in session and "sitename" not in session:
    #     session["Logoname"] = "spidereyes.png"
    #     session["sitename"] = "spidereyes"
    if request.method == "POST":
        data = form.data
        print(form.data)

        if form.validate_on_submit(): #提交数据有效
            session["sitename"] = data["Sitename"]
            filename = form.Logo.data.filename
            if filename:
                DBobject1 = DBObject(sitename=form.Sitename.data, pic_url=form.Logo.data.filename)
                session["Logoname"] = filename
                form.Logo.data.save(os.path.join(app.config["UPLOAD_PATH"], filename))
            else:
                if "Logoname" in session:
                    DBobject1 = DBObject(sitename=session["sitename"], pic_url=session["Logoname"])
                else:
                    DBobject1 = DBObject(sitename=session["sitename"], pic_url=DBObject.query.filter_by(id = 2).first().pic_url)
            db.session.add(DBobject1)
            db.session.commit()
            return redirect("/index")
        else: #提交数据无效
            if "Logoname" in session and "sitename" in session:
                return render_template("settings.html", form=form, name=session['Logoname'], sitename=session["sitename"], desc_value="abcdefg")
            elif "Logoname" in session:
                return render_template("settings.html", form=form, name=session['Logoname'], sitename=DBObject.query.filter_by(id = 2).first().sitename, desc_value="abcdefg")
            elif "sitename" in session:
                return render_template("settings.html", form=form, name=DBObject.query.filter_by(id = 2).first().pic_url, sitename=session['sitename'], desc_value="abcdefg")
            else:
                return render_template("settings.html", form=form,
                                       name=DBObject.query.filter_by(id = 2).first().pic_url,
                                       sitename=DBObject.query.filter_by(id = 2).first().sitename, desc_value="abcdefg")
    else: #get请求
        if "sitename" in session:
            sitecls = Siteclass(session["sitename"])
        sitecls1 = Siteclass(DBObject.query.filter_by(id = 2).first().sitename)
        if "Logoname" in session and "sitename" in session:
            return render_template("settings.html", form=form, name=session['Logoname'], siteclass=sitecls, desc_value="abcdefg")
        elif "Logoname" in session:
            return render_template("settings.html", form=form, name=session['Logoname'], siteclass=sitecls1, desc_value="abcdefg")
        elif "sitename" in session:
            return render_template("settings.html", form=form, name=DBObject.query.filter_by(id = 2).first().pic_url, siteclass=sitecls, desc_value="abcdefg")
        else:
            return render_template("settings.html", form=form,
                                   name=DBObject.query.filter_by(id = 2).first().pic_url,
                                   siteclass=sitecls1, desc_value="abcdefg")


@app.route("/test", methods=["GET"])
def test():
    return "hello" + session["sitename"]

@app.route("/showlogo/<path:filename>", methods=["GET"])
def show_pic(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)