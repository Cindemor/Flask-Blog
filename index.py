from flask import render_template, Flask, views, request, redirect, make_response, session
from DBUtils.PooledDB import PooledDB
import markdown
import cgi
from config import Config
import pymysql
import time
from index_classes import aorp_data, archives_data, index_data
import re
from admin_classes import LoginForm, IntroForm, CookieCheck
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
        cursor.execute("select sitename, githubloc from setting where username = '1004'")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 order by unix_timestamp(article_date) desc")
        for i in cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        cursor.execute("select head, html, unix_timestamp(article_date), author, markdown from article_page"
                       " where ispage = 0 and draft = 0 order by unix_timestamp(article_date) desc")
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
        cursor.execute("select sitename, githubloc from setting where username = '1004'")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0")
        for i in cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        cursor.execute("select substring(article_date, 1, 10), head, html from article_page where ispage = 0 and draft = 0 "
                       "order by unix_timestamp(article_date)")
        result = cursor.fetchall() #选出排序后的文章年与日，标题，html文件名
        cursor.execute("select substring(article_date, 1, 7), count(*) from article_page where ispage = 0 and draft = 0"
                       " group by substring(article_date, 1, 7) order by unix_timestamp(article_date)")
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
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0")
        for i in cursor.fetchall():
            pages.append(dict({'name': i[1], 'href': "../page/" + i[0]}))
        year = time.strftime('%Y', time.localtime(time.time()))

        cursor.execute("select sitename, githubloc from setting where username = '1004'")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        if aname:
            sql = "select markdown, head, substring(article_date, 1, 10), unix_timestamp(article_date), author from article_page " \
                  "where ispage = 0 and username = '1004' and html = '" + aname + "'"
            cursor.execute(sql)
            atitle_post_date_author = cursor.fetchone()
            sql0 = "select html, head from article_page where ispage = 0 and username = '1004' " \
                   "and unix_timestamp(article_date) > " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
            sql1 = "select html, head from article_page where ispage = 0 and username = '1004' " \
                   "and unix_timestamp(article_date) < " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
        elif pname:
            sql = "select markdown, head, substring(article_date, 1, 10), unix_timestamp(article_date), author from article_page " \
                  "where ispage = 1 and username = '1004' and html = '" + pname + "'"
            cursor.execute(sql)
            atitle_post_date_author = cursor.fetchone()
            sql0 = "select html, head from article_page where ispage = 1 and username = '1004' " \
                   "and unix_timestamp(article_date) > " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
            sql1 = "select html, head from article_page where ispage = 1 and username = '1004' " \
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
        print(form.data)
        if request.method == "POST":
            print(form.validate())
            if form.validate():
                db = POOL.connection()
                cursor = db.cursor()
                cursor.execute("select username from admin_")
                usernames = cursor.fetchall()
                print(usernames)
                if (form.username.data,) in usernames:
                    cursor.execute("select password_ from admin_ where username = '" + form.username.data + "'")
                    temp = cursor.fetchone()
                    response = make_response(redirect("/admin/intro"))
                    if temp == (form.password.data,) and form.check.data == True:
                        session["user"] = form.username.data
                        print (session)
                        response.set_cookie("promission", "1", path="/admin", expires=time.time()+604800)
                        return response
                    elif temp == (form.password.data,):
                        print ('yes')
                        session["user"] = form.username.data
                        response.set_cookie("promission", "1", path="/admin")
                        return response
                    else:
                        form.username.data = ""
                        return render_template("login.html", form=form, msg="密码错误！")
                else:
                    form.username.data = ""
                    return render_template("login.html", form=form, msg="输入的账号不存在！")
            else:
                return render_template("login.html", form=form)
        else:
            cookiecheck = CookieCheck("promission", "user")
            print(session)
            print(request.cookies)
            if cookiecheck.check(request, session):
                return redirect("/admin/intro")
            else:
                return render_template("login.html", form=form)

class intro_view(views.View):
    def dispatch_request(self):
        cookiecheck = CookieCheck("promission", "user")
        if cookiecheck.check(request, session):
            intro_form = IntroForm("aaa", "aaa", "aaa", ["aaaa","bbbb"])
            return render_template("introduction.html", form=intro_form)
        else:
            return redirect("/admin")
app.add_url_rule('/', view_func=index_view.as_view('index'), methods=["GET"])
app.add_url_rule('/archives', view_func=archives_view.as_view('archives'), methods=["GET"])
app.add_url_rule('/post/<aname>', view_func=aorp_view.as_view('articles'), methods=["GET"])
app.add_url_rule('/page/<pname>', view_func=aorp_view.as_view('pages'), methods=["GET"])
app.add_url_rule('/admin', view_func=login_view.as_view('login'), methods=["GET", "POST"])
app.add_url_rule('/admin/intro', view_func=intro_view.as_view('introduction'), methods=["GET"])



# @app.route('/post/<article_path>')
# def article(article_path):
#     post = md2html()
#     return render_template('post.html', article = post)
if __name__ == '__main__':
    app.run(debug = True, port = '80')