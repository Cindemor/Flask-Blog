from flask import render_template, Flask, views, request, redirect, make_response, session, send_from_directory
from DBUtils.PooledDB import PooledDB
import markdown
import cgi
from config import Config
import pymysql
import time
from index_classes import aorp_data, archives_data, index_data
import re
from admin_classes import LoginForm, IntroForm, SettingForm, aorpForm, aorpWriteForm
import os
from datetime import timedelta

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

class index_view(views.View):
    def md2html(self, name):
        code_head = '\n<div class="Code">'
        code_tail = '</div>\n'
        have_head = False
        input_file = open(app.config["MD_PATH"] + "\\" + name, 'r', encoding='utf-8')
        input_fullfile = open(app.config["MD_PATH"] + "\\" + name, 'r', encoding='utf-8')
        full = input_fullfile.read()
        line = input_file.readline()
        text = '...'
        if '<!--more-->' in full:
            text = ''
            while line:
                if '<!--more-->' in line:
                    break
                if '```' == line[:3]:
                    if have_head == False:
                        line = code_head + '\n<code>'
                        have_head = True
                    else:
                        line = '</code>\n' + code_tail
                        have_head = False
                elif have_head:
                    line = cgi.escape(line)
                text += line
                line = input_file.readline()
        input_fullfile.close()
        input_file.close()
        return (markdown.markdown(text))

    def dispatch_request(self):
        db = POOL.connection()
        cursor = db.cursor()
        pages = list()
        posts = list()
        year = time.strftime('%Y',time.localtime(time.time()))
        cursor.execute("select sitename, githubloc from setting")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1 order by unix_timestamp(article_date) desc")
        for i in cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        cursor.execute("select head, html, unix_timestamp(article_date), author, markdown from article_page"
                       " where ispage = 0 and draft = 0 and open_degree = 1 order by unix_timestamp(article_date) desc")
        post_infor = cursor.fetchall()
        for j in post_infor:
            post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(j[2]))
            text = self.md2html(j[4])
            posts.append(dict({'title':j[0], 'href':'post/'+j[1], 'ad':j[3]+" 发布于 "+post_time, 'more':text}))
        cursor.execute("select logo from setting")
        picname = cursor.fetchone()[0]
        form = index_data(title, pages, github, posts, year, picname)
        cursor.close()
        db.close()
        return render_template('index.html', data = form)

class archives_view(views.View):
    def dispatch_request(self):
        db = POOL.connection()
        cursor = db.cursor()
        posts = list()
        date1 = list()
        pages = list()
        year = time.strftime('%Y',time.localtime(time.time()))
        cursor.execute("select sitename, githubloc from setting")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1")
        for i in cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        cursor.execute("select substring(article_date, 1, 10), head, html from article_page where ispage = 0 and draft = 0 "
                       " and open_degree = 1 order by unix_timestamp(article_date)")
        result = cursor.fetchall() #选出排序后的文章年与日，标题，html文件名
        cursor.execute("select substring(article_date, 1, 7), count(*) from article_page where ispage = 0 and draft = 0"
                       " and open_degree = 1 group by substring(article_date, 1, 7) order by unix_timestamp(article_date)")
        number = cursor.fetchall() #选出排序后的文章年月以及各分组的长度
        for i in number:
            RE = "([0-9]+?)-([0-9]+)"
            RE_list = re.findall(RE, i[0])
            date1.append(RE_list[0][0] + "年" + RE_list[0][1] + "月")
        v = 0
        for j in range(len(date1)):
            l = dict()
            temp = list()
            l["time"] = date1[j]
            max = number[j][1]
            for v1 in range(max):
                temp.append(dict({'date':result[v][0], 'title':result[v][1], 'href':"post/" + result[v][2]}))
                v += 1
            l["articles"] = temp
            posts.append(l)
        cursor.execute("select logo from setting")
        picname = cursor.fetchone()[0]
        form = index_data(title, pages, github, posts, year, picname)
        cursor.close()
        db.close()
        return render_template('archives.html', data = form)


class aorp_view(views.View):
    def md2html(self, name):
        code_head = '\n<div class="Code">'
        code_tail = '</div>\n'
        have_head = False
        input_file = open(app.config["MD_PATH"] + "\\" + name, 'r', encoding='utf-8')
        line = input_file.readline()
        text = ''
        while line:
            if '```' == line[:3]:
                if have_head == False:
                    line = code_head + '\n<code>'
                    have_head = True
                else:
                    line = '</code>\n' + code_tail
                    have_head = False
            elif have_head:
                line = cgi.escape(line)
            text += line
            line = input_file.readline()
        input_file.close()
        return (markdown.markdown(text))
    def dispatch_request(self, aname = '', pname = ''):
        db = POOL.connection()
        cursor = db.cursor()
        pages = list()
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1")
        for i in cursor.fetchall():
            pages.append(dict({'name': i[1], 'href': "../page/" + i[0]}))
        year = time.strftime('%Y', time.localtime(time.time()))

        cursor.execute("select sitename, githubloc from setting")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        if aname:
            sql = "select markdown, head, substring(article_date, 1, 10), unix_timestamp(article_date), author from article_page " \
                  "where ispage = 0 and draft = 0 and open_degree = 1 and html = '" + aname + "'"
            cursor.execute(sql)
            atitle_post_date_author = cursor.fetchone()
            sql0 = "select html, head from article_page where ispage = 0 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) > " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
            sql1 = "select html, head from article_page where ispage = 0 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) < " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
        elif pname:
            sql = "select markdown, head, substring(article_date, 1, 10), unix_timestamp(article_date), author from article_page " \
                  "where ispage = 1 and html = '" + pname + "'"
            cursor.execute(sql)
            atitle_post_date_author = cursor.fetchone()
            sql0 = "select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) > " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
            sql1 = "select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) < " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
        if cursor.execute(sql0) > 0:
            html_head = cursor.fetchone()
            next_html = html_head[0]
            next_head = html_head[1]
        else:
            next_html = "../"
            next_head = "没有下一个(回首页)"
        if cursor.execute(sql1) > 0:
            html_head = cursor.fetchone()
            last_html = html_head[0]
            last_head = html_head[1]
        else:
            last_html = "../"
            last_head = "没有上一个(回首页)"
        post = self.md2html(atitle_post_date_author[0])
        atitle = atitle_post_date_author[1]
        RE = "([0-9]+?)-([0-9]+?)-([0-9]+)"
        RE_list = re.findall(RE, atitle_post_date_author[2])
        author_date = "本文由作者 " + atitle_post_date_author[4] + " 发表于 " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(atitle_post_date_author[3]))
        date = RE_list[0][1] + '月' + RE_list[0][2] + ", " + RE_list[0][0]
        cursor.execute("select logo from setting")
        picname = cursor.fetchone()[0]
        form = aorp_data(title, pages, github, atitle, date, author_date, last_head, last_html, next_head, next_html, year, post, picname)
        cursor.close()
        db.close()
        return render_template('post.html', data = form)

class login_view(views.View):
    def dispatch_request(self):
        form = LoginForm()
        temp = setting_view()
        sitename = temp.get_sitename()
        if request.method == "POST":
            if form.validate():
                db = POOL.connection()
                cursor = db.cursor()
                cursor.execute("select username from admin_")
                usernames = cursor.fetchall()
                if (form.username.data,) in usernames:
                    cursor.execute("select password_ from admin_ where username = '" + form.username.data + "'")
                    temp = cursor.fetchone()
                    response = make_response(redirect("/admin/intro"))
                    if temp == (form.password.data,) and form.check.data == True:
                        session["user"] = form.username.data
                        session.permanent = True
                        return response
                    elif temp == (form.password.data,):
                        session["user"] = form.username.data
                        return response
                    else:
                        form.username.data = ""
                        return render_template("login.html", form=form, msg="账号或密码错误！", sitename=sitename)
                else:
                    form.username.data = ""
                    return render_template("login.html", form=form, msg="账号或密码错误！", sitename=sitename)
                cursor.close()
                db.close()
            else:
                return render_template("login.html", form=form, sitename=sitename)
        else:
            if session.get('user'):
                return redirect("/admin/intro")
            else:
                return render_template("login.html", form=form, sitename=sitename)


class intro_view(views.View):
    def dispatch_request(self):
        if session.get('user'):
            db = POOL.connection()
            cursor = db.cursor()
            cursor.execute("select sitename from setting")
            sitename = cursor.fetchall()[0][0]
            cursor.execute("select count(*), ispage from article_page group by ispage order by ispage")
            nums = cursor.fetchall()
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
            cursor.execute(
                "select html, head, article_date from article_page where ispage = 0 and draft = 0 and open_degree = 1 "
                "order by unix_timestamp(article_date) desc limit 3")
            a = cursor.fetchall()
            cursor.execute(
                "select html, head, article_date from article_page where ispage = 1 and draft = 0 and open_degree = 1 "
                "order by unix_timestamp(article_date) desc limit 3")
            b = cursor.fetchall()
            articles = list()
            pages = list()
            for i in a:
                articles.append(dict({'title': i[1], 'href': i[0], 'date': i[2]}))
            for j in b:
                pages.append(dict({'title': j[1], 'href': j[0], 'date': j[2]}))
            logoname = setting_view().get_logoname(cursor)
            cursor.close()
            db.close()
            intro_form = IntroForm(sitename, post_num, page_num, articles, pages)
            return render_template("introduction.html", form=intro_form, logoname=logoname)
        else:
            return redirect("/admin")


class setting_view(views.View):
    def dispatch_request(self):
        if session.get('user'):
            form = SettingForm()
            db = POOL.connection()
            cursor = db.cursor()
            if request.method == "POST":
                if form.validate_on_submit():
                    if form.Logo.data.filename:
                        RE = ".*(\..*)$" # 取文件后缀
                        now = str(time.time()) # 时间戳作为文件名
                        filename =  now + re.findall(RE, form.Logo.data.filename)[0]
                        form.Logo.data.save(os.path.join(app.config["UPLOAD_PATH"], filename))
                        cursor.execute("select logo from setting")
                        past_name = cursor.fetchone()[0]  # 删除当前库中的文件
                        os.remove(app.config["UPLOAD_PATH"] + "\\" + past_name)
                        try:
                            sql = "update setting set logo = '" + filename + "', sitename = '" + form.Sitename.data \
                                   + "', sitedesc = '" + form.Sitedesc.data + "', siteloc = '" + form.Siteloc.data \
                                   + "', githubloc = '" + form.Sitegitloc.data + "', gongxinbeian = '" + form.Sitebeian0.data \
                                   + "', gonganbeian = '" + form.Sitebeian1.data + "'"
                            cursor.execute(sql)
                            db.commit()
                        except:
                            db.rollback()
                        return render_template("settings.html", form=form, fname=filename)
                    else:
                        try:
                            cursor.execute("update setting set sitename = '" + form.Sitename.data
                                           + "', sitedesc = '" + form.Sitedesc.data + "', siteloc = '" + form.Siteloc.data
                                           + "', githubloc = '" + form.Sitegitloc.data + "', gongxinbeian = '" + form.Sitebeian0.data
                                           + "', gonganbeian = '" + form.Sitebeian1.data + "'")
                            db.commit()
                        except:
                            db.rollback()
                        cursor.execute("select logo from setting")
                        return render_template("settings.html", form=form, fname=cursor.fetchone()[0], logoname=self.get_logoname(cursor))
                else:
                    form_fname = self.search_database(cursor, form)
                    return render_template("settings.html", form=form_fname[0], fname=form_fname[1], logoname=self.get_logoname(cursor))
            else:
                form_fname = self.search_database(cursor, form)
                return render_template("settings.html", form=form_fname[0], fname=form_fname[1], logoname=self.get_logoname(cursor))
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
    def get_logoname(self, cursor):
        cursor.execute("select logo from setting")
        return cursor.fetchone()[0]
    def get_sitename(self):
        db = POOL.connection()
        sql = "select sitename from setting"
        cursor = db.cursor()
        cursor.execute(sql)
        temp = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return temp

class aorplist_view(views.View):
    def __init__(self):
        self.__get = setting_view()
    def dispatch_request(self, type):
        if session.get('user'):
            db = POOL.connection()
            cursor = db.cursor()
            logoname = setting_view().get_logoname(cursor)
            if type == "page":
                if "now_page" in session:
                    string = session["now_page"]
                else:
                    string = 0
                sql = "select html, head, article_date, author, draft from article_page where ispage = 1 order by article_date desc limit " + str(string) + ", 7" #根用户的权限
                cursor.execute(sql)
                query_result = cursor.fetchall()
                result = list()
                for i in query_result:
                    form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3], i[0])
                    result.append(form)
                return render_template("page_manager.html", contents = result, sitename = self.__get.get_sitename(), logoname=logoname)
            elif type == "post":
                if "now_post" in session:
                    string = session["now_post"]
                else:
                    string = 0
                sql = "select html, head, article_date, author, draft from article_page where ispage = 0 order by article_date desc limit " + str(string) + ", 7" #根用户的权限
                cursor.execute(sql)
                query_result = cursor.fetchall()
                result = list()
                for i in query_result:
                    form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3], i[0])
                    result.append(form)
                return render_template("article_manager.html", contents = result, sitename = self.__get.get_sitename(), logoname=logoname)
            else:
                return redirect("/none")
        else:
            return redirect("/admin")


class aorpcreate_view(views.View):
    def dispatch_request(self, type):
        if session.get('user'):
            form = aorpWriteForm()
            db = POOL.connection()
            cursor = db.cursor()
            logoname = setting_view().get_logoname(cursor)
            if request.method == "POST": #post请求
                author_default = self.get_author() #从admin_表中获取所有作者名
                filename = form.Filename.data
                if type == "post":
                    cursor.execute("select html from article_page where ispage = 0")
                    if (filename + ".html",) not in cursor.fetchall():
                        ispage = str(0)
                    else:
                        form.Filename.data = ""
                        return render_template("article_create.html", form=form, siteip=request.host_url, sitename=setting_view().get_sitename(),
                                               msg="不可出现同名文件", author=author_default[0], default=author_default[1], logoname=logoname)
                elif type == "page":
                    cursor.execute("select html from article_page where ispage = 1")
                    if (filename + ".html",) not in cursor.fetchall():
                        ispage = str(1)
                    else:
                        form.Filename.data = ""
                        return render_template("page_create.html", form=form, siteip=request.host_url, sitename=setting_view().get_sitename(),
                                               msg="不可出现同名文件", author=author_default[0], default=author_default[1], logoname=logoname)
                else:
                    cursor.close()
                    db.close()
                    return redirect("/none")
                header = form.Header.data
                date = form.Date.data
                author = form.Author.data
                md = form.Article.data.encode('utf-8')
                md_name = str(time.time()) + ".md"
                with open(app.config["MD_PATH"] + "\\" + md_name, "wb") as file:
                    file.write(md)
                if form.Opendegree.data == "o":
                    draft = str(0)
                elif form.Opendegree.data == "d":
                    draft = str(1)
                else:
                    return redirect("/none")
                sql = "insert into article_page values ('" + session["user"] + "', '" + filename + ".html', '" + header \
                + "', '" + date + "', " + "1, '" + author + "', " + ispage + "," + draft + ",'" + md_name + "')"
                try:
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                return redirect("../../admin/" + type + "/edit/" + filename + ".html")
            else:
                author_default = self.get_author()
                if type == "post":
                    form.Opendegree.data = "o"
                    return render_template("article_create.html", form=form,
                                           siteip=request.host_url, sitename=setting_view().get_sitename(), authors=author_default[0],
                                           default=author_default[1], logoname=logoname)
                elif type == "page":
                    form.Opendegree.data = "o"
                    return render_template("page_create.html", form=form,
                                           siteip=request.host_url, sitename=setting_view().get_sitename(), authors=author_default[0],
                                           default=author_default[1], logoname=logoname)
                else:
                    return redirect("/none")
        else:
            return redirect("/admin")
    def get_author(self):
        db = POOL.connection()
        sql = "select name from admin_"
        cursor = db.cursor()
        cursor.execute(sql)
        temp = cursor.fetchall()
        cursor.close()
        db.close()
        return (temp, temp[0][0])

class aorpedit_view(views.View):
    def __init__(self):
        self.__get = aorpcreate_view()
    def dispatch_request(self, type, filename):
        if session.get('user'):
            form = aorpWriteForm()
            db = POOL.connection()
            cursor = db.cursor()
            logoname = setting_view().get_logoname(cursor)
            if request.method == "POST":
                if type == "post":
                    sql = "update article_page set html = '" + form.Filename.data + ".html', head = '" + form.Header.data \
                          + "',draft = "+ ("1" if form.Opendegree.data == "d" else "0")
                    sql += ", author = '" + form.Author.data + "', article_date ='" + form.Date.data + "' where html = '" + \
                           filename + "' and ispage = 0"
                    sql1 = "select markdown from article_page where html = '" + filename + "' and ispage = 0"
                elif type == "page":
                    sql = "update article_page set html = '" + form.Filename.data + ".html', head = '" + form.Header.data \
                          + "',draft = "+ ("1" if form.Opendegree.data == "d" else "0")
                    sql += ", author = '" + form.Author.data + "', article_date ='" + form.Date.data + "' where html = '" + \
                           filename + "' and ispage = 1"
                    sql1 = "select markdown from article_page where html = '" + filename + "' and ispage = 1"
                else:
                    return redirect("/none")
                try:
                    cursor.execute(sql1)
                    with open(app.config["MD_PATH"] + "\\" + cursor.fetchone()[0], 'wb') as file:
                        file.write(form.Article.data.encode('utf-8')) #消除换行叠加问题
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                if type == "post":
                    return redirect("/admin/post/edit/" + form.Filename.data + ".html")
                else:
                    return redirect("/admin/page/edit/" + form.Filename.data + ".html")
            else:
                if type == "post":
                    sql = "select html, head, unix_timestamp(article_date), draft, " \
                          "author, markdown from article_page where html = '" + filename + "' and ispage = 0"
                elif type == "page":
                    sql = "select html, head, unix_timestamp(article_date), draft, " \
                          "author, markdown from article_page where html = '" + filename + "' and ispage = 1"
                else:
                    return redirect("/none")
                cursor.execute(sql)
                temp = cursor.fetchone()
                RE = "(.*).html"
                fname = re.findall(RE, temp[0])[0]
                form.Header.data = temp[1]
                form.Filename.data = fname
                form.Opendegree.data = "d" if temp[3] else "o"
                form.Author.data = temp[4]
                form.Date.data = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(temp[2]))
                with open(app.config["MD_PATH"] + "\\" + temp[5], 'r', encoding="utf-8") as file:
                    form.Article.data = file.read()
                if type == "post":
                    return render_template("article_edit.html", path=request.url, form=form,
                                       sitename=setting_view().get_sitename(), siteip=request.host_url,
                                       authors=self.__get.get_author()[0], default=self.__get.get_author()[1], logoname=logoname)
                else:
                    return render_template("page_edit.html", path=request.url, form=form,
                                       sitename=setting_view().get_sitename(), siteip=request.host_url,
                                       authors=self.__get.get_author()[0], default=self.__get.get_author()[1], logoname=logoname)
        else:
            return redirect("/admin")

class aorpdelete_view(views.View):
    def dispatch_request(self, type, filename):
        if session.get('user'):
            db = POOL.connection()
            cursor = db.cursor()
            sql0 = "select markdown from article_page where html = '" + filename + "' and ispage = 0 and username = '" + session["user"] + "'"
            sql1 = "select markdown from article_page where html = '" + filename + "' and ispage = 1 and username = '" + session["user"] + "'"
            if type == "post":
                sql = "delete from article_page where html = '" + filename + "' and ispage = 0 and username = '" + session["user"] + "'"
                try:
                    cursor.execute(sql0)
                    os.remove(app.config["MD_PATH"] + "\\" + cursor.fetchone()[0])
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                return redirect("/admin/post/list")
            elif type == "page":
                sql = "delete from article_page where html = '" + filename + "' and ispage = 1 and username = '" + session["user"] + "'"
                try:
                    cursor.execute(sql1)
                    os.remove(app.config["MD_PATH"] + "\\" + cursor.fetchone()[0])
                    cursor.execute(sql)
                    db.commit()
                except:
                    db.rollback()
                return redirect(("/admin/page/list"))
            else:
                return redirect("/none")
        else:
            return redirect("/admin")

@app.route("/showlogo/<path:filename>", methods=["GET"])
def show_pic(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)

@app.route("/add", methods=["POST"])
def load_content():
    db = POOL.connection()
    cursor = db.cursor()
    if request.form["type"] == "post":
        session["now_post"] = request.form["num"]
        sql = "select html, head, article_date, author, draft from article_page where ispage = 0 order by article_date desc limit " + request.form["num"] + ", 7"
    elif request.form["type"] == "page":
        session["now_page"] = request.form["num"]
        sql = "select html, head, article_date, author, draft from article_page where ispage = 1 order by article_date desc limit " + request.form["num"] + ", 7"
    else:
        return redirect("/404")
    cursor.execute(sql)
    query_result = cursor.fetchall()
    result = list()
    for i in query_result:
        form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3], i[0])
        result.append(form)
    return render_template("manager_add.html", contents=result)

app.add_url_rule('/', view_func=index_view.as_view('index'), methods=["GET"])
app.add_url_rule('/archives', view_func=archives_view.as_view('archives'), methods=["GET"])
app.add_url_rule('/post/<aname>', view_func=aorp_view.as_view('articles'), methods=["GET"])
app.add_url_rule('/page/<pname>', view_func=aorp_view.as_view('pages'), methods=["GET"])
app.add_url_rule('/admin', view_func=login_view.as_view('login'), methods=["GET", "POST"])
app.add_url_rule('/admin/intro', view_func=intro_view.as_view('introduction'), methods=["GET"])
app.add_url_rule('/admin/setting', view_func=setting_view.as_view('settings'), methods=["GET", "POST"])
app.add_url_rule('/admin/<type>/list', view_func=aorplist_view.as_view('aorplist'), methods=["GET", "POST"])
app.add_url_rule('/admin/<type>/create', view_func=aorpcreate_view.as_view('aorpcreate'), methods=["POST", "GET"])
app.add_url_rule('/admin/<type>/delete/<filename>', view_func=aorpdelete_view.as_view('aorpdelete'), methods=["POST"])
app.add_url_rule('/admin/<type>/edit/<filename>', view_func=aorpedit_view.as_view('aorpedit'), methods=["POST", "GET"])

if __name__ == '__main__':
    app.run(debug = True, port = '80')