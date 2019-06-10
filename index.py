from flask import render_template, Flask, views
import markdown
import cgi
from config import Config
import pymysql
import time
from db_class import aorp_data, archives_data, index_data
import re

app = Flask(__name__)
app.config.from_object(Config)


class index_view(views.View):
    def dispatch_request(self):
        db = pymysql.connect(host="localhost", user="root", password="zq", port=3306, database="article_management")
        cursor = db.cursor()
        pages = list()
        posts = list()
        year = time.strftime('%Y',time.localtime(time.time()))
        cursor.execute("select sitename, githubloc from setting where username = '1004'")
        git_title = cursor.fetchall()[0]
        title = git_title[0]
        github = git_title[1]
        cursor.execute("select html, head from article_page where ispage = 1 and draft = 0")
        for i in cursor.fetchall():
            pages.append(dict({'name':i[1], 'href':"page/"+i[0]}))
        cursor.execute("select head, html, unix_timestamp(article_date), author, markdown from article_page where ispage = 0 and draft = 0")
        post_infor = cursor.fetchall()
        print(post_infor)
        for j in post_infor:
            post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(j[2]))
            print(post_time)
            posts.append(dict({'title':j[0], 'href':'post/'+j[1], 'ad':j[3]+" 发布于 "+post_time, 'more':j[4]}))
        fuck = index_data(title, pages, github, posts, year)
        return render_template('index.html', data = fuck)

class archives_view(views.View):
    def dispatch_request(self):
        db = pymysql.connect(host="localhost", user="root", password="zq", port=3306, database="article_management")
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
        cursor.execute("select substring(article_date, 1, 10), head, html from article_page where ispage = 0 and draft = 0 order by unix_timestamp(article_date)")
        result = cursor.fetchall()
        print(result)
        cursor.execute("select substring(article_date, 1, 7), count(*) from article_page where ispage = 0 and draft = 0 group by substring(article_date, 1, 7) order by unix_timestamp(article_date)")
        number = cursor.fetchall()
        print(number)
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
                temp.append(dict({'date':result[v][0], 'title':result[v][1], 'href':result[v][2]}))
                v += 1
            l["articles"] = temp
            posts.append(l)
        fuck = index_data(title, pages, github, posts, year)
        return render_template('archives.html', data = fuck)


class aorp_view(views.View):
    def md2html(self):
        code_head = '\n<div class="Code">'
        code_tail = '</div>\n'
        have_head = False
        input_file = open('testmd.md', 'r', encoding='utf-8')
        line = input_file.readline()
        text = ''
        while line:
            if '```' in line:
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
        return (markdown.markdown(text))
    def dispatch_request(self, aname = '', pname = ''):
        if aname:
            post = self.md2html()
            fuck = aorp_data('a',[{'name':'b1','href':'./aaa'},{'name':'b2','href':'./aaa'}],'c','d','e','f','g','h','i','j','k',post)
            return render_template('post.html' , data = fuck)
        elif pname:
            post = self.md2html()
            fuck = aorp_data('a',[{'name':'b1','href':'./aaa'},{'name':'b2','href':'./aaa'}],'c','d','e','f','g','h','i','j','k',post)
            return render_template('post.html' , data = fuck)

app.add_url_rule('/', view_func=index_view.as_view('index'))
app.add_url_rule('/archives', view_func=archives_view.as_view('archives'))
app.add_url_rule('/post/<aname>', view_func=aorp_view.as_view('articles'))
app.add_url_rule('/page/<pname>', view_func=aorp_view.as_view('pages'))


# @app.route('/post/<article_path>')
# def article(article_path):
#     post = md2html()
#     return render_template('post.html', article = post)

if __name__ == '__main__':
    app.run(debug = True, port = '80')