from flask import render_template, Flask, views, request, redirect, session, send_from_directory
from DBUtils.PooledDB import PooledDB
import markdown
import cgi
from config import Config
import pymysql
import time
from index_classes import aorp_data, archives_data, index_data
import re
from management import setting_view, aorpcreate_view, aorport_delete_view, aorport_edit_view, intro_view, login_view, tagcreate_view, aorplist_view, taglist_view
from admin_classes import aorpForm

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
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

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
        pages = list()
        posts = list()
        year = time.strftime('%Y',time.localtime(time.time()))
        self.cursor.execute("select sitename, githubloc from setting")
        git_title = self.cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        self.cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1 order by unix_timestamp(article_date) desc")
        for i in self.cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        self.cursor.execute("select head, html, unix_timestamp(article_date), author, markdown from article_page"
                       " where ispage = 0 and draft = 0 and open_degree = 1 order by unix_timestamp(article_date) desc")
        post_infor = self.cursor.fetchall()
        for j in post_infor:
            post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(j[2]))
            text = self.md2html(j[4])
            posts.append(dict({'title':j[0], 'href':'post/'+j[1], 'ad':j[3]+" 发布于 "+post_time, 'more':text}))
        self.cursor.execute("select logo from setting")
        picname = self.cursor.fetchone()[0]
        form = archives_data(title, pages, github, posts, year, picname)
        return render_template('index.html', data = form)

    def __del__(self):
        self.cursor.close()
        self.db.close()


class archives_view(views.View):
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

    def dispatch_request(self):
        posts = list()
        date1 = list()
        pages = list()
        year = time.strftime('%Y',time.localtime(time.time()))
        self.cursor.execute("select sitename, githubloc from setting")
        git_title = self.cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        self.cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1")
        for i in self.cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        self.cursor.execute("select substring(article_date, 1, 10), head, html from article_page where ispage = 0 and draft = 0 "
                       " and open_degree = 1 order by unix_timestamp(article_date)")
        result = self.cursor.fetchall() #选出排序后的文章年与日，标题，html文件名
        self.cursor.execute("select substring(article_date, 1, 7), count(*) from article_page where ispage = 0 and draft = 0"
                       " and open_degree = 1 group by substring(article_date, 1, 7) order by unix_timestamp(article_date)")
        number = self.cursor.fetchall() #选出排序后的文章年月以及各分组的长度
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
        self.cursor.execute("select logo from setting")
        picname = self.cursor.fetchone()[0]
        form = index_data(title, pages, github, posts, year, picname)
        self.cursor.close()
        self.db.close()
        return render_template('archives.html', data = form)

    def __del__(self):
        self.cusor.close()
        self.db.close()


class aorp_view(views.View):
    def __init__(self):
        self.db = POOL.connection()
        self.cursor = self.db.cursor()

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
        pages = list()
        self.cursor.execute("select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1")
        for i in self.cursor.fetchall():
            pages.append(dict({'name': i[1], 'href': "../page/" + i[0]}))
        year = time.strftime('%Y', time.localtime(time.time()))
        self.cursor.execute("select sitename, githubloc from setting")
        git_title = self.cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        if aname:
            sql = "select markdown, head, substring(article_date, 1, 10), unix_timestamp(article_date), author from article_page " \
                  "where ispage = 0 and draft = 0 and open_degree = 1 and html = '" + aname + "'"
            self.cursor.execute(sql)
            atitle_post_date_author = self.cursor.fetchone()
            sql0 = "select html, head from article_page where ispage = 0 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) > " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
            sql1 = "select html, head from article_page where ispage = 0 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) < " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
        elif pname:
            sql = "select markdown, head, substring(article_date, 1, 10), unix_timestamp(article_date), author from article_page " \
                  "where ispage = 1 and html = '" + pname + "'"
            self.cursor.execute(sql)
            atitle_post_date_author = self.cursor.fetchone()
            sql0 = "select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) > " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
            sql1 = "select html, head from article_page where ispage = 1 and draft = 0 and open_degree = 1 " \
                   "and unix_timestamp(article_date) < " + str(atitle_post_date_author[3]) + " order by unix_timestamp(article_date) limit 1"
        if self.cursor.execute(sql0) > 0:
            html_head = self.cursor.fetchone()
            next_html = html_head[0]
            next_head = html_head[1]
        else:
            next_html = "../"
            next_head = "没有下一个(回首页)"
        if self.cursor.execute(sql1) > 0:
            html_head = self.cursor.fetchone()
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
        self.cursor.execute("select logo from setting")
        picname = self.cursor.fetchone()[0]
        form = aorp_data(title, pages, github, atitle, date, author_date, last_head, last_html, next_head, next_html, year, post, picname)
        return render_template('post.html', data = form)

    def __del__(self):
        self.cursor.close()
        self.db.close()


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
app.add_url_rule('/admin/<type>/list', view_func=aorplist_view.as_view('aorplist'), methods=["GET"])
app.add_url_rule('/admin/<type>/create', view_func=aorpcreate_view.as_view('aorpcreate'), methods=["POST", "GET"])
app.add_url_rule('/admin/<type>/delete/<filename>', view_func=aorport_delete_view.as_view('aorpdelete'), methods=["POST"])
app.add_url_rule('/admin/<type>/edit/<filename>', view_func=aorport_edit_view.as_view('aorpedit'), methods=["POST", "GET"])
app.add_url_rule('/admin/tag/list', view_func=taglist_view.as_view('taglist'), methods=["GET"])
app.add_url_rule('/admin/tag/create', view_func=tagcreate_view.as_view('tagcreate'), methods=["POST", "GET"])

if __name__ == '__main__':
    app.run(debug = True, port = '80')