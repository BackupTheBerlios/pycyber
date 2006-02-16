from gettext import gettext

import database
import config

def default_model(req):
  req.default_response()
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<style type="text/css"><!--
body { font-family:Verdana; }
a { text-decoration:none; color:#000099; }
a:hover { font-weight:bold; }
table.panel { background:#eeeeee; width:100%%; border-style:solid; border-width:1px; padding:5px; border-color:#aaaaaa; }
input { width:70px; border: 1px solid #aaaaaa; color:#444444; background:#f5f5f5; }
input.text { width:200px; border: 1px solid #aaaaaa; color:#444444; background:#ffffff; }
li { list-style-type:none; }
--></style>
</head>
<body>
<table class="panel"><tr><td align="center">
<a href="add">[%s]</a> <a href="queryname">[%s]</a> <a href="queryid">[%s]</a> <a href="topuse">[%s]</a>
</td></tr></table><br />
""" % (gettext('add'), gettext('query by name'), gettext('query by id'), gettext('bigger costumers')))

def index(req):
  default_model(req)
  req.wfile.write("""
</body>
</html>
""")

def add(req):
  default_model(req)
  req.wfile.write("""
<div align="center">
<form action="doadd" method="post">
<table>
<tr><td>%s:</td><td><input type="text" class="text" name="name" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="birthday" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="address" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="telephone" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="credit" value="0" style="width:70px;" /> min</td></tr>
</table><br />
<input type="submit" value="OK" />
</form>
</div>
</body>
</html>
""" % (gettext('Name'), gettext('Birthday'), gettext('Address'), gettext('Telephone'), gettext('Initial credit')))
  
def doadd(req):
  default_model(req)
  cu = database.cx.cursor()
  values = []
  for x in ('name','birthday','address','telephone','credit'):
    try:
      values.append(req.form[x].value)
    except:
      values.append('')
  try:
    values[4] = int(values[4])
  except:
    values[4] = 0
  cu.execute('insert into costumers (name,birthday,address,telephone,credit,total_use) values (?,?,?,?,?,0);', values)
  database.cx.commit()
  cu.execute('select id from costumers order by id desc limit 1;')
  id = cu.fetchone()[0]
  cu.close()
  req.wfile.write("""
<div align="center">
%s<br />
<h2>%d-%s</h2>
</div>
</body>
</html>
""" % (gettext("Your costumer's code is"), id, database.gen_usercode(id)))

def query_model(req, fieldname, action):
  default_model(req)
  req.wfile.write("""  
<script language="javascript" type="text/javascript" src="/ajax/js"></script>
<div align="center">
<form onsubmit="t(0);return false;">
%s: <input class="text" type="text" name="q" id="q" />
</form>
<div id="l">
</div>
</div>
<script language="javascript" type="text/javascript"><!--
lt=' ';
req=null;
function onA(){
  if(req.readyState==4&&req.status==200)
    document.getElementById('l').innerHTML=req.responseText;
}
function t(a){
  if(lt!=document.getElementById('q').value){
    lt=document.getElementById('q').value;
    req=xmlHTTPAsyncRequest('%s?q='+lt,'GET',null,onA);
  }
  if(a) window.setTimeout('t(1)',2500);
}
window.setTimeout('t(1)',1000);
//--></script>
</body>
</html>
""" % (fieldname, action))

def queryname(req):
  query_model(req, gettext('Name'), 'doqname')

def doqname(req):
  req.default_response()
  if req.qs.has_key('q'):
    q = req.qs['q'][0]
    s = ''
    if len(q) < 5:
      s = ' limit 20'
    q = q.replace("'","''")+'%'
    cu = database.cx.cursor()
    cu.execute("select id,name from costumers where name like ? order by name%s;" % s, (q,))
    a = cu.fetchone()
    if a:
      req.wfile.write('<ul>\n')
    else:
      req.wfile.write(gettext('No results found.'))
      cu.close()
      return
    while a:
      req.wfile.write("""<li><a href="edit?id=%d">%s</a></li>
""" % (a[0], a[1].encode('utf-8')))
      a = cu.fetchone()
    cu.close()
    if s != '':
      req.wfile.write('<li>...</li>\n')
    req.wfile.write('</ul>')
  else:
    req.wfile.write(gettext('Please, type the beginning of the name.'))

def queryid(req):
  query_model(req, gettext('Code'), 'doqid')
  
def doqid(req):
  req.default_response()
  if req.qs.has_key('q'):
    q = req.qs['q'][0]
    if '-' in q:
      q = q.split('-')[0]
    try:
      q = int(q)
    except:
      req.wfile.write(gettext('Invalid code.'))
      return
    cu = database.cx.cursor()
    cu.execute('select name from costumers where id=?;', (q,))
    a = cu.fetchone()
    if a:
      req.wfile.write("""<ul>
<li><a href="edit?id=%d">%s</a></li>
</ul>
""" % (q, a[0].encode('utf-8')))
    else:
      req.wfile.write(gettext('No results found.'))
    cu.close()
  else:
    req.wfile.write(gettext('Please, type the costumer code.'))
    
def topuse(req):
  query_model(req, gettext('Number of results'), 'doqtop')
  
def doqtop(req):
  req.default_response()
  if req.qs.has_key('q'):
    q = req.qs['q'][0]
    try:
      q = int(q)
    except:
      req.wfile.write(gettext('Invalid number.'))
      return
    cu = database.cx.cursor()
    cu.execute('select id,name,total_use from costumers order by total_use desc, name asc limit %d;' % (q))
    a = cu.fetchone()
    if a:
      req.wfile.write('<ul>\n')
    else:
      req.wfile.write(gettext('No results found.'))
      cu.close()
      return
    while a:
      if a[2] > 60:
        if a[2] % 60 == 0:
          usetime = '%d h' % (a[2]/60)
        else:
          usetime = '%d h %d min' % (a[2]/60, a[2]%60)
      else:
        usetime = '%d min' % a[2]
      req.wfile.write("""
<li><a href="edit?id=%d">%s</a><br />[%s]</li>
""" % (a[0], a[1].encode('utf-8'), usetime))
      a = cu.fetchone()
    cu.close()
    req.wfile.write('<li>&nbsp;</li><li><a href="resettop">[%s]</a></li></ul>' % gettext('reset counter'))
  else:
    req.wfile.write(gettext('Please, type the number of costumers you want to display.'))

def resettop(req):
  default_model(req)
  cu = database.cx.cursor()
  cu.execute('update costumers set total_use=0;')
  cu.close()
  req.wfile.write("""
<div align="center">
%s
</div>
""" % gettext('The total service use counter was reset for all costumers successfuly.'))

def edit(req):
  try:
    id = int(req.qs['id'][0])
  except:
    return
  default_model(req)
  cu = database.cx.cursor()
  cu.execute('select * from costumers where id=%d;' % id)
  a = cu.fetchone()
  cu.close()
  req.wfile.write("""
<div align="center">
<form action="doedit?id=%d" method="post">
<table>
<tr><td>%s:</td><td><input type="text" class="text" value="%d-%s" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="name" value="%s" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="birthday" value="%s" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="address" value="%s" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="telephone" value="%s" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="credit" value="%d" style="width:70px;" /> min</td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="total_use" value="%d" style="width:70px;" /> min</td></tr>
</table><br />
<input type="submit" value="OK" />
</form>
</div>
</body>
</html>
""" % (id,
  gettext('User code'), id, database.gen_usercode(id),
  gettext('Name'), a[1].encode('utf-8'),
  gettext('Birthday'), a[2].encode('utf-8'),
  gettext('Address'), a[3].encode('utf-8'),
  gettext('Telephone'), a[4].encode('utf-8'),
  gettext('Credit'), a[5],
  gettext('Total Use'), a[6],
))

def doedit(req):
  try:
    id = int(req.qs['id'][0])
  except:
    return
  default_model(req)
  values = []
  for x in ('name','birthday','address','telephone','credit','total_use'):
    try:
      values.append(req.form[x].value)
    except:
      values.append('')
  try:
    values[4] = int(values[4])
  except:
    values[4] = 0
  try:
    values[5] = int(values[5])
  except:
    values[5] = 0
  cu = database.cx.cursor()
  cu.execute('update costumers set name=?,birthday=?,address=?,telephone=?,credit=?,total_use=? where id=%d;' % id, values)
  database.cx.commit()
  cu.close()
  req.wfile.write("""
<div align="center">
%s
</div>
""" % gettext('Costumer information was successfuly updated.'))
