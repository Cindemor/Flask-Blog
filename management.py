from admin_classes import LoginForm, IntroForm, SettingForm, aorpForm, aorpWriteForm, TagForm
from flask import render_template, Flask, views, request, redirect, make_response, session
import pymysql
import os
import re
import time
from config import Config
from DBUtils.PooledDB import PooledDB

app = Flask(__name__)

app.config.from_object(Config)
POOL = PooledDB(
    creator = pymysql,
    host = "127.0.0.1",
    port = 3306,
    user = "root",
    password = "zq",
    database = "article_management",
    charset="utf8"
)
class login_view(views.View):
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()
        self.form = LoginForm()
        self.__get = setting_view()

    def dispatch_request(self):
        if request.method == "POST":
            if self.form.validate():
                self.cursor.execute("select username from admin_")
                usernames = self.cursor.fetchall()
                if (self.form.username.data,) in usernames:
                    self.cursor.execute("select password_ from admin_ where username = '" + self.form.username.data + "'")
                    temp = self.cursor.fetchone()
                    response = make_response(redirect("/admin/intro"))
                    if temp == (self.form.password.data,) and self.form.check.data == True:
                        session["user"] = self.form.username.data
                        session.permanent = True
                        return response
                    elif temp == (self.form.password.data,):
                        session["user"] = self.form.username.data
                        return response
                    else:
                        self.form.username.data = ""
                        return render_template("login.html", form=self.form, msg="账号或密码错误！", sitename=self.__get.get_sitename())
                else:
                    self.form.username.data = ""
                    return render_template("login.html", form=self.form, msg="账号或密码错误！", sitename=self.__get.get_sitename())
            else:
                return render_template("login.html", form=self.form, sitename=self.__get.get_sitename())
        else:
            if session.get('user'):
                return redirect("/admin/intro")
            else:
                return render_template("login.html", form=self.form, sitename=self.__get.get_sitename())

    def __del__(self):
        self.cursor.close()
        self.db.close()


class intro_view(views.View):
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self):
        if session.get('user'):
            self.cursor.execute("select sitename from setting")
            sitename = self.cursor.fetchall()[0][0]
            self.cursor.execute("select count(*), ispage from article_page group by ispage order by ispage")
            nums = self.cursor.fetchall()
            if len(nums) > 1:
                post_num = nums[0][0]
                page_num = nums[1][0]
            elif len(nums) > 0:
                if nums[0][1]:
                    post_num = 0
                    page_num = nums[0][0]
                else:
                    post_num = nums[0][0]
                    page_num = 0
            else:
                intro_form = IntroForm(sitename, 0, 0, [], [])
                return render_template("introduction.html", form=intro_form)
            self.cursor.execute(
                "select html, head, article_date from article_page where ispage = 0 and draft = 0 and open_degree = 1 "
                "order by unix_timestamp(article_date) desc limit 3")
            a = self.cursor.fetchall()
            self.cursor.execute(
                "select html, head, article_date from article_page where ispage = 1 and draft = 0 and open_degree = 1 "
                "order by unix_timestamp(article_date) desc limit 3")
            b = self.cursor.fetchall()
            articles = list()
            pages = list()
            for i in a:
                articles.append(dict({'title': i[1], 'href': i[0], 'date': i[2]}))
            for j in b:
                pages.append(dict({'title': j[1], 'href': j[0], 'date': j[2]}))
            logoname = setting_view().get_logoname()
            self.cursor.close()
            self.db.close()
            intro_form = IntroForm(sitename, post_num, page_num, articles, pages)
            return render_template("introduction.html", form=intro_form, logoname=logoname)
        else:
            return redirect("/admin")

    def __del__(self):
        self.cursor.close()
        self.db.close()


class setting_view(views.View):
    def __init__(self):
        self.form = SettingForm()
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self):
        if session.get('user'):
            if request.method == "POST":
                if self.form.validate_on_submit():
                    if self.form.Logo.data.filename:
                        RE = ".*(\..*)$" # 取文件后缀
                        now = str(time.time()) # 时间戳作为文件名
                        filename =  now + re.findall(RE, self.form.Logo.data.filename)[0]
                        self.form.Logo.data.save(os.path.join(app.config["UPLOAD_PATH"], filename))
                        self.cursor.execute("select logo from setting")
                        past_name = self.cursor.fetchone()[0]  # 删除当前库中的文件
                        os.remove(app.config["UPLOAD_PATH"] + "\\" + past_name)
                        try:
                            sql = "update setting set logo = '" + filename + "', sitename = '" + self.form.Sitename.data \
                                   + "', sitedesc = '" + self.form.Sitedesc.data + "', siteloc = '" + self.form.Siteloc.data \
                                   + "', githubloc = '" + self.form.Sitegitloc.data + "', gongxinbeian = '" + self.form.Sitebeian0.data \
                                   + "', gonganbeian = '" + self.form.Sitebeian1.data + "'"
                            self.cursor.execute(sql)
                            self.db.commit()
                        except:
                            self.db.rollback()
                        return render_template("settings.html", form=self.form, fname=filename)
                    else:
                        try:
                            self.cursor.execute("update setting set sitename = '" + self.form.Sitename.data
                                           + "', sitedesc = '" + self.form.Sitedesc.data + "', siteloc = '" + self.form.Siteloc.data
                                           + "', githubloc = '" + self.form.Sitegitloc.data + "', gongxinbeian = '" + self.form.Sitebeian0.data
                                           + "', gonganbeian = '" + self.form.Sitebeian1.data + "'")
                            self.db.commit()
                        except:
                            self.db.rollback()
                        self.cursor.execute("select logo from setting")
                        return render_template("settings.html", form=self.form, fname=self.cursor.fetchone()[0], logoname=self.get_logoname())
                else:
                    form_fname = self.search_database(self.cursor, self.form)
                    return render_template("settings.html", form=form_fname[0], fname=form_fname[1], logoname=self.get_logoname())
            else:
                form_fname = self.search_database(self.cursor, self.form)
                return render_template("settings.html", form=form_fname[0], fname=form_fname[1], logoname=self.get_logoname())
        else:
            return redirect("/admin")

    def search_database(self, cursor, form):
        cursor.execute("select sitename, lower(logo), sitedesc, siteloc, githubloc, gongxinbeian, gonganbeian from setting")
        result = cursor.fetchone()
        form.Sitename.data = result[0]
        fname = result[1]
        form.Sitedesc.data = result[2]
        form.Siteloc.data = result[3]
        form.Sitegitloc.data = result[4]
        form.Sitebeian0.data = result[5]
        form.Sitebeian1.data = result[6]
        return (form, fname)

    def get_logoname(self):
        self.cursor.execute("select logo from setting")
        return self.cursor.fetchone()[0]

    def get_sitename(self):
        sql = "select sitename from setting"
        self.cursor.execute(sql)
        temp = self.cursor.fetchone()[0]
        return temp

    def __del__(self):
        self.cursor.close()
        self.db.close()


class aorplist_view(views.View):
    def __init__(self):
        self.__get = setting_view()
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self, type):
        if session.get('user'):
            if type == "page":
                if "now_page" in session:
                    string = session["now_page"]
                else:
                    string = 0
                sql = "select html, head, article_date, author, draft from article_page where ispage = 1 order by article_date desc limit " + str(string) + ", 7" #根用户的权限
                self.cursor.execute(sql)
                query_result = self.cursor.fetchall()
                result = list()
                for i in query_result:
                    form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3], i[0])
                    result.append(form)
                return render_template("page_manager.html", contents = result, sitename = self.__get.get_sitename(), logoname=self.__get.get_logoname())
            elif type == "post":
                if "now_post" in session:
                    string = session["now_post"]
                else:
                    string = 0
                sql = "select html, head, article_date, author, draft from article_page where ispage = 0 order by article_date desc limit " + str(string) + ", 7" #根用户的权限
                self.cursor.execute(sql)
                query_result = self.cursor.fetchall()
                result = list()
                for i in query_result:
                    form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3], i[0])
                    result.append(form)
                return render_template("article_manager.html", contents = result, sitename = self.__get.get_sitename(), logoname=self.__get.get_logoname())
            else:
                return redirect("/none")
        else:
            return redirect("/admin")

    def __del__(self):
        print("执行析构函数")
        self.cursor.close()
        self.db.close()


class aorpcreate_view(views.View):
    def __init__(self):
        print("执行构造函数")
        self.db = POOL.connection()
        self.cursor = self.db.cursor()
        self.form = aorpWriteForm()
        self.get = setting_view()

    def dispatch_request(self, type):
        if session.get('user'):
            logoname = self.get.get_logoname()
            if request.method == "POST": #post请求
                author_default = self.get_author() #从admin_表中获取所有作者名
                filename = self.form.Filename.data
                if type == "post":
                    self.cursor.execute("select html from article_page where ispage = 0")
                    if (filename + ".html",) not in self.cursor.fetchall():
                        ispage = str(0)
                    else:
                        self.form.Filename.data = ""
                        return render_template("article_create.html", form=self.form, siteip=request.host_url, sitename=setting_view().get_sitename(),
                                               msg="不可出现同名文件", author=author_default[0], default=author_default[1], logoname=logoname)
                elif type == "page":
                    self.cursor.execute("select html from article_page where ispage = 1")
                    if (filename + ".html",) not in self.cursor.fetchall():
                        ispage = str(1)
                    else:
                        self.form.Filename.data = ""
                        return render_template("page_create.html", form=self.form, siteip=request.host_url, sitename=setting_view().get_sitename(),
                                               msg="不可出现同名文件", author=author_default[0], default=author_default[1], logoname=logoname)
                else:
                    return redirect("/none")
                header = self.form.Header.data
                date = self.form.Date.data
                author = self.form.Author.data
                md = self.form.Article.data.encode('utf-8')
                md_name = str(time.time()) + ".md"
                with open(app.config["MD_PATH"] + "\\" + md_name, "wb") as file:
                    file.write(md)
                if self.form.Opendegree.data == "o":
                    draft = str(0)
                elif self.form.Opendegree.data == "d":
                    draft = str(1)
                else:
                    return redirect("/none")
                sql = "insert into article_page values ('" + session["user"] + "', '" + filename + ".html', '" + header \
                + "', '" + date + "', " + "1, '" + author + "', " + ispage + "," + draft + ",'" + md_name + "')"
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                except:
                    self.db.rollback()
                return redirect("../../admin/" + type + "/edit/" + filename + ".html")
            else:
                author_default = self.get_author()
                if type == "post":
                    self.form.Opendegree.data = "o"
                    return render_template("article_create.html", form=self.form,
                                           siteip=request.host_url, sitename=setting_view().get_sitename(), authors=author_default[0],
                                           default=author_default[1], logoname=logoname)
                elif type == "page":
                    self.form.Opendegree.data = "o"
                    return render_template("page_create.html", form=self.form,
                                           siteip=request.host_url, sitename=setting_view().get_sitename(), authors=author_default[0],
                                           default=author_default[1], logoname=logoname)
                else:
                    return redirect("/none")
        else:
            return redirect("/admin")

    def get_author(self):
        sql = "select name from admin_"
        self.cursor.execute(sql)
        temp = self.cursor.fetchall()
        return (temp, temp[0][0])

    def __del__(self):
        print("执行析构函数")
        self.cursor.close()
        self.db.close()

class aorpedit_view(views.View):
    def __init__(self):
        self.__get = aorpcreate_view()
        self.form = aorpWriteForm()
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self, type, filename):
        if session.get('user'):
            logoname = setting_view().get_logoname()
            if request.method == "POST":
                if type == "post":
                    sql = "update article_page set html = '" + self.form.Filename.data + ".html', head = '" + self.form.Header.data \
                          + "',draft = "+ ("1" if self.form.Opendegree.data == "d" else "0")
                    sql += ", author = '" + self.form.Author.data + "', article_date ='" + self.form.Date.data + "' where html = '" + \
                           filename + "' and ispage = 0"
                    sql1 = "select markdown from article_page where html = '" + filename + "' and ispage = 0"
                elif type == "page":
                    sql = "update article_page set html = '" + self.form.Filename.data + ".html', head = '" + self.form.Header.data \
                          + "',draft = "+ ("1" if self.form.Opendegree.data == "d" else "0")
                    sql += ", author = '" + self.form.Author.data + "', article_date ='" + self.form.Date.data + "' where html = '" + \
                           filename + "' and ispage = 1"
                    sql1 = "select markdown from article_page where html = '" + filename + "' and ispage = 1"
                else:
                    return redirect("/none")
                try:
                    self.cursor.execute(sql1)
                    with open(app.config["MD_PATH"] + "\\" + self.cursor.fetchone()[0], 'wb') as file:
                        file.write(self.form.Article.data.encode('utf-8')) #消除换行叠加问题
                    self.cursor.execute(sql)
                    self.db.commit()
                except:
                    self.db.rollback()
                if type == "post":
                    return redirect("/admin/post/edit/" + self.form.Filename.data + ".html")
                else:
                    return redirect("/admin/page/edit/" + self.form.Filename.data + ".html")
            else:
                if type == "post":
                    sql = "select html, head, unix_timestamp(article_date), draft, " \
                          "author, markdown from article_page where html = '" + filename + "' and ispage = 0"
                elif type == "page":
                    sql = "select html, head, unix_timestamp(article_date), draft, " \
                          "author, markdown from article_page where html = '" + filename + "' and ispage = 1"
                else:
                    return redirect("/none")
                self.cursor.execute(sql)
                temp = self.cursor.fetchone()
                RE = "(.*).html"
                fname = re.findall(RE, temp[0])[0]
                self.form.Header.data = temp[1]
                self.form.Filename.data = fname
                self.form.Opendegree.data = "d" if temp[3] else "o"
                self.form.Author.data = temp[4]
                self.form.Date.data = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(temp[2]))
                with open(app.config["MD_PATH"] + "\\" + temp[5], 'r', encoding="utf-8") as file:
                    self.form.Article.data = file.read()
                if type == "post":
                    return render_template("article_edit.html", path=request.url, form=self.form,
                                       sitename=setting_view().get_sitename(), siteip=request.host_url,
                                       authors=self.__get.get_author()[0], default=self.__get.get_author()[1], logoname=logoname)
                else:
                    return render_template("page_edit.html", path=request.url, form=self.form,
                                       sitename=setting_view().get_sitename(), siteip=request.host_url,
                                       authors=self.__get.get_author()[0], default=self.__get.get_author()[1], logoname=logoname)
        else:
            return redirect("/admin")

    def __del__(self):
        self.cursor.close()
        self.db.close()

class aorpdelete_view(views.View):
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self, type, filename):
        if session.get('user'):
            sql0 = "select markdown from article_page where html = '" + filename + "' and ispage = 0 and username = '" + session["user"] + "'"
            sql1 = "select markdown from article_page where html = '" + filename + "' and ispage = 1 and username = '" + session["user"] + "'"
            if type == "post":
                sql = "delete from article_page where html = '" + filename + "' and ispage = 0 and username = '" + session["user"] + "'"
                try:
                    self.cursor.execute(sql0)
                    os.remove(app.config["MD_PATH"] + "\\" + self.cursor.fetchone()[0])
                    self.cursor.execute(sql)
                    self.db.commit()
                except:
                    self.db.rollback()
                return redirect("/admin/post/list")
            elif type == "page":
                sql = "delete from article_page where html = '" + filename + "' and ispage = 1 and username = '" + session["user"] + "'"
                try:
                    self.cursor.execute(sql1)
                    os.remove(app.config["MD_PATH"] + "\\" + self.cursor.fetchone()[0])
                    self.cursor.execute(sql)
                    self.db.commit()
                except:
                    self.db.rollback()
                return redirect(("/admin/page/list"))
            else:
                return redirect("/none")
        else:
            return redirect("/admin")
    def __del__(self):
        self.cursor.close()
        self.db.close()


class tagcreate_view(views.View):
    def __init__(self):
        self.get = setting_view()
        self.form = TagForm()
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self):
        print(self.form.data)
        if session.get('user'):
            if request.method == "POST":
                if self.form.validate():
                    sql1 = "select count(*) from tag"
                    self.cursor.execute(sql1)
                    num = str(int(self.cursor.fetchone()[0]) + 1)
                    sql2 = "insert into tag values ('" + num + "', '" + self.form.Name.data + "', '" + self.form.Shortname.data + "')"
                    try:
                        self.cursor.execute(sql2)
                        self.db.commit()
                        return render_template("tag_create.html", form = self.form, sitename = self.get.get_sitename(), logoname = self.get.get_logoname(), message="提交成功")
                    except:
                        self.db.rollback()
                        self.form.Name.data = ""
                        return render_template("tag_create.html", form = self.form, sitename = self.get.get_sitename(), logoname = self.get.get_logoname(), message="重复标签名")
                else:
                    return "NONE"
            else:
                return render_template("tag_create.html", form = self.form, sitename = self.get.get_sitename(), logoname = self.get.get_logoname())
        else:
            return redirect("/admin")
class taglist_view(views.View):
    def __init__(self):
        self.get = setting_view()
    def dispatch_request(self):
        return render_template("tag_manager.html", sitename = self.get.get_sitename(), logoname = self.get.get_logoname())





