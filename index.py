from flask import render_template, Flask, views
import markdown
import cgi

app = Flask(__name__)

# pages
# [
#     {
#         'name':'xxx',
#         'href':'aaa'
#     },
# ]

# posts
# [
#     {
#         'title':'xxx',
#         'href':'xxx',
#         'ad':'xxx',
#         'more':'xxx'
#     },
# ]

# mp
# [
#     {
#         'time':'xxx',
#         'articles': [
#             {
#                 'title':'xxx',
#                 'href':'xxx',
#                 'date':'xxx'
#             },
#         ]
#     },
# ]

class index_data():
    def __init__(self, s_title, pages, github, posts, year):
        self.__sitetitle = s_title #str
        self.__pages = pages # list
        self.__github = github #str
        self.__posts = posts #list
        self.__cpyear = year #str
    def get_attr(self, id):
        if id == 0:
            return self.__sitetitle
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.__github
        elif id == 3:
            return self.__posts
        elif id == 4:
            return self.__cpyear

class archives_data():
    def __init__(self, s_title, pages, github, mp, year):
        self.__sitetitle = s_title #str
        self.__pages = pages # list
        self.__github = github #str
        self.__mp = mp #list
        self.__cpyear = year #str
    def get_attr(self, id):
        if id == 0:
            return self.__sitetitle
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.__github
        elif id == 3:
            return self.__mp
        elif id == 4:
            return self.__cpyear

class aorp_data():
    def __init__(self, s_title, pages, github, title, date, info, ptitle, phref, ntitle, nhref, year, content):
        self.__sitetitle = s_title #str
        self.__pages = pages # list
        self.__github = github #str
        self.__title = title # str
        self.__date = date # str
        self.__info = info # str
        self.__ptitle = ptitle # str
        self.__phref = phref # str
        self.__ntitle = ntitle # str
        self.__nhref = nhref # str
        self.__cpyear = year #str
        self.__content = content #str
    def get_attr(self, id):
        if id == 0:
            return self.__sitetitle
        elif id == 1:
            return self.__pages
        elif id == 2:
            return self.__github
        elif id == 3:
            return self.__title
        elif id == 4:
            return self.__date
        elif id == 5:
            return self.__info
        elif id == 6:
            return self.__ptitle
        elif id == 7:
            return self.__phref
        elif id == 8:
            return self.__ntitle
        elif id == 9:
            return self.__nhref
        elif id == 10:
            return self.__cpyear
        elif id == 11:
            return self.__content


class index_view(views.View):
    def dispatch_request(self):
        a = [
            {
                'title':'xxx',
                'href':'xxx',
                'ad':'xxx',
                'more':'xxx'
            },
            {
                'title':'xxx1',
                'href':'xxx1',
                'ad':'xxx',
                'more':'xxx'
            },
            {
                'title':'xxx2',
                'href':'xxx2',
                'ad':'xxx2',
                'more':'xxx'
            }
        ]
        fuck = index_data('aa',[{'name':'fuck1','href':'./aaa'},{'name':'fuck2','href':'./aaa'},{'name':'fuck3','href':'./aaa'}],'a',a,'a')
        return render_template('index.html', data = fuck)

class archives_view(views.View):
    def dispatch_request(self):
        a = [
            {
                'time':'1xxx',
                'articles': [
                    {
                        'title':'axxx',
                        'href':'xxx',
                        'date':'xxx'
                    },
                    {
                        'title':'bxxx',
                        'href':'xxx',
                        'date':'xxx'
                    },
                    {
                        'title':'cxxx',
                        'href':'xxx',
                        'date':'xxx'
                    }
                ]
            },
            {
                'time':'2xxx',
                'articles': [
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    }
                ]
            },
            {
                'time':'3xxx',
                'articles': [
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    },
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    }
                ]
            },
            {
                'time':'4xxx',
                'articles': [
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    },
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    },
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    },
                    {
                        'title':'xxx',
                        'href':'xxx',
                        'date':'xxx'
                    }
                ]
            },
        ]
        fuck = index_data('aa',[{'name':'fuck1','href':'./aaa'},{'name':'fuck2','href':'./aaa'},{'name':'fuck3','href':'./aaa'}],'a',a,'a')
        return render_template('archives.html', data = fuck)


class aorp_view(views.View):
    def dispatch_request(self, aname = '', pname = ''):
        if aname:
            post = md2html()
            fuck = aorp_data('a',[{'name':'b1','href':'./aaa'},{'name':'b2','href':'./aaa'}],'c','d','e','f','g','h','i','j','k',post)
            return render_template('post.html' , data = fuck)
        elif pname:
            post = md2html()
            fuck = aorp_data('a',[{'name':'b1','href':'./aaa'},{'name':'b2','href':'./aaa'}],'c','d','e','f','g','h','i','j','k',post)
            return render_template('post.html' , data = fuck)

app.add_url_rule('/', view_func=index_view.as_view('index'))
app.add_url_rule('/archives', view_func=archives_view.as_view('archives'))
app.add_url_rule('/post/<aname>', view_func=aorp_view.as_view('articles'))
app.add_url_rule('/page/<pname>', view_func=aorp_view.as_view('pages'))


def md2html():
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

# @app.route('/post/<article_path>')
# def article(article_path):
#     post = md2html()
#     return render_template('post.html', article = post)

if __name__ == '__main__':
    app.run(debug = True, port = '80')