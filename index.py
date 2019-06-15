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
        input_file = open(name, 'r', encoding='utf-8')
        input_fullfile = open(name, 'r', encoding='utf-8')
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
        print(post_infor)
        for j in post_infor:
            post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(j[2]))
            text = self.md2html(j[4])
            posts.append(dict({'title':j[0], 'href':'post/'+j[1], 'ad':j[3]+" 发布于 "+post_time, 'more':text}))
        fuck = index_data(title, pages, github, posts, year)
        cursor.close()
        db.close()
        return render_template('index.html', data = fuck)

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
        print(date1)
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
        fuck = index_data(title, pages, github, posts, year)
        cursor.close()
        db.close()
        return render_template('archives.html', data = fuck)


class aorp_view(views.View):
    def md2html(self, name):
        code_head = '\n<div class="Code">'
        code_tail = '</div>\n'
        have_head = False
        input_file = open(name, 'r', encoding='utf-8')
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
        print(next_head)
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
        fuck = aorp_data(title, pages, github, atitle, date, author_date, last_head, last_html, next_head, next_html, year, post)
        cursor.close()
        db.close()
        return render_template('post.html', data = fuck)

class login_view(views.View):
    def dispatch_request(self):
        form = LoginForm()
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
                        return render_template("login.html", form=form, msg="账号或密码错误！")
                else:
                    form.username.data = ""
                    return render_template("login.html", form=form, msg="账号或密码错误！")
                cursor.close()
                db.close()
            else:
                return render_template("login.html", form=form)
        else:
            if session.get('user'):
                return redirect("/admin/intro")
            else:
                return render_template("login.html", form=form)

class intro_view(views.View):
    def dispatch_request(self):
        if session.get('user'):
            db = POOL.connection()
            cursor = db.cursor()
            cursor.execute("select sitename from setting")
            sitename = cursor.fetchall()[0][0]
            cursor.execute("select count(*) from article_page group by ispage order by ispage")
            nums = cursor.fetchall()
            post_num = nums[0][0]
            page_num = nums[1][0]
            cursor.execute("select html, head, substring(article_date, 1, 10) from article_page where ispage = 0 and draft = 0 and open_degree = 1 "
            "order by unix_timestamp(article_date) desc limit 5")
            articles = list()
            for i in cursor.fetchall():
                articles.append(dict({'title': i[1], 'href': i[0], 'date': i[2]}))
            cursor.close()
            db.close()
            intro_form = IntroForm(sitename, post_num, page_num, articles)
            return render_template("introduction.html", form=intro_form, sitename=self.get_sitename())
        else:
            return redirect("/admin")
    def get_sitename(self):
        db = POOL.connection()
        sql = "select sitename from setting"
        cursor = db.cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]

class setting_view(views.View):
    def dispatch_request(self):
        if session.get('user'):
            form = SettingForm()
            print(form.data)
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
                        return render_template("settings.html", form=form, fname=cursor.fetchone()[0])
                else:
                    form_fname = self.search_database(cursor, form)
                    return render_template("settings.html", form=form_fname[0], fname=form_fname[1])
            else:
                form_fname = self.search_database(cursor, form)
                return render_template("settings.html", form=form_fname[0], fname=form_fname[1])
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

class aorplist_view(views.View):
    def dispatch_request(self, type):
        if session.get('user'):
            db = POOL.connection()
            cursor = db.cursor()
            if type == "page":
                sql = "select html, head, article_date, author, draft from article_page where ispage = 1 and author = 'spider' order by article_date desc"
                cursor.execute(sql)
                query_result = cursor.fetchall()
                result = list()
                for i in query_result:
                    form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3])
                    result.append(form)
                return render_template("page_manager.html", contents = result, sitename = self.get_sitename())
            elif type == "post":
                sql = "select html, head, article_date, author, draft from article_page where ispage = 0 and author = 'spider' order by article_date desc"
                cursor.execute(sql)
                query_result = cursor.fetchall()
                result = list()
                for i in query_result:
                    form = aorpForm(i[1], "草稿" if i[4] else "已发布", i[2], i[3])
                    result.append(form)
                return render_template("article_manager.html", contents = result, sitename = self.get_sitename())
            else:
                return redirect("/none")
        else:
            return redirect("/admin")
    def get_sitename(self):
        db = POOL.connection()
        sql = "select sitename from setting"
        cursor = db.cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]

class aorpcreate_view(views.View):
    def dispatch_request(self, type):
        if session.get('user'):
            form = aorpWriteForm()
            if request.method == "POST":
                if type == "post":
                    pass
                elif type == "page":
                    pass
                else:
                    pass
            else:
                if type == "post":
                    return render_template("article_create.html", form=form, siteip=request.host_url, sitename=self.get_sitename())
                elif type == "page":
                    return render_template("page_create.html", form=form, siteip=request.host_url, sitename=self.get_sitename())
                else:
                    return redirect("/none")
        else:
            return redirect("/admin")
    def get_sitename(self):
        db = POOL.connection()
        sql = "select sitename from setting"
        cursor = db.cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]

@app.route("/showlogo/<path:filename>", methods=["GET"])
def show_pic(filename):
    return send_from_directory(app.config["UPLOAD_PATH"], filename)

app.add_url_rule('/', view_func=index_view.as_view('index'), methods=["GET"])
app.add_url_rule('/archives', view_func=archives_view.as_view('archives'), methods=["GET"])
app.add_url_rule('/post/<aname>', view_func=aorp_view.as_view('articles'), methods=["GET"])
app.add_url_rule('/page/<pname>', view_func=aorp_view.as_view('pages'), methods=["GET"])
app.add_url_rule('/admin', view_func=login_view.as_view('login'), methods=["GET", "POST"])
app.add_url_rule('/admin/intro', view_func=intro_view.as_view('introduction'), methods=["GET"])
app.add_url_rule('/admin/setting', view_func=setting_view.as_view('settings'), methods=["GET", "POST"])
app.add_url_rule('/admin/<type>/list', view_func=aorplist_view.as_view('aorplist'), methods=["GET", "POST"])
app.add_url_rule('/admin/<type>/create', view_func=aorpcreate_view.as_view('aorpcreate'), methods=["POST", "GET"])


# @app.route('/post/<article_path>')
# def article(article_path):
#     post = md2html()
#     return render_template('post.html', article = post)
if __name__ == '__main__':
    app.run(debug = True, port = '80')