import shutil
import time
import os
import re
import urllib
from gettext import gettext

import config
import cfgloader
import database
import pckiller

pcs = { }
alerts = { }
alertid = 0

def_route = None
transf_measure = None

def addalert(msg):
  global alertid
  if type(msg) != str:
    return
  id = alertid
  alerts[id] = msg
  alertid += 1
  if alertid > 500:
    alertid = 0
  return id

def alertimg(req):
  req.send_response(200)
  req.send_header('Content-Type', 'image/png')
  req.send_header('Connection', 'close')
  req.end_headers()
  f = file('alert.png', 'rb')
  shutil.copyfileobj(f, req.wfile)
  f.close()

def rmalert(req):
  alerts.pop(int(req.qs['id'][0]))
  index(req)

def index(req):
  
  global def_route, transf_measure
  
  req.default_response()
  
  # Get default route
  if def_route is None: 
    f = os.popen('/sbin/route')
    l = f.readlines()
    f.close()
    for x in l:
      a = x.split()
      if a[0] == 'default':
        def_route = a[7]
  
  # Get RX/TX bytes
  tstamp = time.time()
  f = os.popen('/sbin/ifconfig %s' % def_route)
  l = f.readlines()
  f.close()
  expr = re.compile('^[^:]+:([0-9]+)[^:]+:([0-9]+)')
  for x in l:
    a = expr.search(x)
    if a:
      net_rx, net_tx = [int(x) for x in a.groups()]

  # Measure transference speed
  if transf_measure is None:
    speed_rx, speed_tx = 0.0, 0.0
  else:
    speed_rx = float(net_rx - transf_measure[1]) / (1024.0 * (tstamp - transf_measure[0]))
    speed_tx = float(net_tx - transf_measure[2]) / (1024.0 * (tstamp - transf_measure[0]))
  
  # Store information for next measure
  transf_measure = (tstamp, net_rx, net_tx)
  
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<style type="text/css"><!--
body { font-family:Verdana; }
a { text-decoration:none; color:#000099; }
a:hover { font-weight:bold; }
table.panel { background:#eeeeee; width:100%%; border-style:solid; border-width:1px; padding:5px; border-color:#aaaaaa; }
table.pcs { width:100%%; border-spacing:3px; }
td.pcs { border-style:solid; border-width:1px; padding:4px; border-color:#dddddd; text-align:center; }
th.pcs { background:#f5f5f5; border-style:solid; border-width:1px; padding:4px; border-color:#dddddd; }
--></style>
<meta http-equiv="refresh" content="%d;index" />
</head>
<body>
<table class="panel"><td width="100%%" align="right">[<b>DOWN</b> %.1f kb/s] [<b>UP</b> %.1f kb/s] [<b>%s</b>]</td></table><br />
""" % (config.refresh_time, speed_rx, speed_tx, time.strftime('%H:%M:%S')))

  # Show alerts
  for x in alerts:
    req.wfile.write("""
<table class="panel"><tr><td><img src="alertimg" /></td>
<td width="100%%">%s</td>
<td><a href="rmalert?id=%d">[ok]</a></td></tr></table><br />
""" % (alerts[x], x))

  req.wfile.write("""
<table class="pcs">
<tr><th class="pcs">%s</th><th class="pcs">%s</th><th class="pcs">%s</th><th class="pcs">%s</th></tr>
""" % (gettext('Computer'), gettext('User'), gettext('Start'), gettext('End')))

  for x in pcs:
    req.wfile.write("""
<tr><td class="pcs"><a href="change?%s" target="_blank">%s</a></td>
<td class="pcs">%s</td>
<td class="pcs">%s</td>
<td class="pcs">%s</td></tr>
""" % (urllib.urlencode({'id':x}), x, pcs[x][0], pcs[x][1], pcs[x][2]))

  req.wfile.write("""
</table><br />
<table class="panel"><tr><td align="center">
<a href="addpc" target="_blank">[%s]</a>
<a href="/costumers/index" target="_blank">[%s]</a>
<a href="/configuration/index" target="_blank">[%s]</a>
</td></tr></table>
</body>
</html>
""" % (gettext('add pc'), gettext('costumers'), gettext('configuration')))

def addpc(req):
  req.default_response()
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<style type="text/css"><!--
body { font-family:Verdana; }
select { width:200px; border: 1px solid #aaaaaa; color:#444444; }
input { width:70px; border: 1px solid #aaaaaa; color:#444444; background:#f5f5f5; }
input.text { width:200px; border: 1px solid #aaaaaa; color:#444444; background:#ffffff; }
table.panel { background:#eeeeee; width:100%%; border-style:solid; border-width:1px; padding:5px; border-color:#aaaaaa; }
--></style>
<script language="javascript" type="text/javascript" src="/ajax/js"></script>
<script language="javascript" type="text/javascript"><!--
lt='';
req=null;
c=0;
credits=0;
hourprice=%f;
function parsehour(s){
  a=s.match(/^([0-9]+):([0-9]+)$/);
  if(a==null)
    return null;
  return parseInt(a[1],10)*60 + parseInt(a[2],10)
}
function diffhour(f,i){
  r=f-i;
  if(r<0)r+=24*60;
  return r;
}
function refdisp(){
  if((f=parsehour(document.getElementById('end').value))==null){
    document.getElementById('end').value='';
    return;
  }
  if((i=parsehour(document.getElementById('start').value))==null){
    document.getElementById('start').value='';
    return;
  }
  document.getElementById('price').value=Math.round((diffhour(f,i)-credits)*hourprice/0.60)/100.0;
}
function onA(){
  if(req.readyState==4&&req.status==200){
    document.getElementById('l').innerHTML=req.responseText;
    credits+=c;
    refdisp();
  }
}
function t(a){
  c=0;
  if(a!=''){
    c=parseInt(a,10);
    a='&d='+a
  }
  req=xmlHTTPAsyncRequest('getuser?id='+document.getElementById('user').value+a,'GET',null,onA);
}
//--></script>
</head>
<body>
<div id="l">
</div><br />
<div align="center">
<form action="doaddpc" method="post">
<table>
<tr><td>%s:</td><td><select name="computer">
""" % (cfgloader.cfg['hourprice'], gettext('Computer')))
  for x in cfgloader.cfg['ips']:
    if not pcs.has_key(x):
      req.wfile.write("""<option value="%s">%s</option>
""" % (x, x))
  req.wfile.write("""</select></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="user" id="user" onchange="t('')" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="start" id="start" value="%s" onchange="refdisp()" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="end" id="end" onchange="refdisp()" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" id="price" /></td></tr>
</table><br />
<input type="submit" value="OK" />
</form>
</div>
</body>
</html>
""" % (gettext('User Code'), gettext('Start'), time.strftime('%H:%M'), gettext('End'), gettext('Price')))

def invalid_usercode(req):
  req.wfile.write("""
<td><img src="alertimg" /></td><td width="100%%">%s</td>
""" % gettext('The user code is invalid.'))

def getuser(req):
  if not req.qs.has_key('id'):
    return
  if req.qs.has_key('d'):
    try:
      d = int(req.qs['d'][0])
      id = int(req.qs['id'][0].split('-')[0])
    except:
      req.send_response(500)
      req.send_header('Connection', 'close')
      req.end_headers()
      return
    cu = database.cx.cursor()
    cu.execute('select credit from costumers where id=%d;' % id)
    credit = cu.fetchone()[0]
    if credit >= d:
      cu.execute('update costumers set credit=credit-%d where id=%d;' % (d, id))
      database.cx.commit()
    else:
      req.send_response(500)
      req.send_header('Connection', 'close')
      req.end_headers()
      cu.close()
      return
    cu.close()
  req.default_response()
  req.wfile.write('<table class="panel"><tr>')
  try:
    id,digit = req.qs['id'][0].split('-')
    id = int(id)
  except:
    invalid_usercode(req)
  else:
    if digit != database.gen_usercode(id):
      invalid_usercode(req)
    else:
      cu = database.cx.cursor()
      cu.execute('select name,credit from costumers where id=%d' % id)
      a = cu.fetchone()
      cu.close()
      if a:
        if a[1] < 60:
          credit = '%d min' % a[1]
        else:
          min = a[1]%60
          if min > 0:
            credit = '%d h %d min' % (a[1]/60, min)
          else:
            credit = '%d h' % (a[1]/60)
        req.wfile.write("""<td align="center"><b>%s</b><table>
<tr><td>%s:</td><td>%s</td></tr>
<tr><td>%s:</td><td>%s</td></tr>
</table>
""" % (gettext('Costumer'), gettext('Name'), a[0].encode('utf-8'), gettext('Credit'), credit))
        if(a[1] > 0):
          req.wfile.write("""
<input type="text" class="text" style="width:70px;" id="d" /> min&nbsp;&nbsp;
<input type="button" value="%s" style="width:100px;" onclick="t(document.getElementById('d').value)" />
""" % gettext('Deduct'))
        req.wfile.write('</td>')
      else:
        invalid_usercode(req)
  req.wfile.write('</tr></table>')

def h2ts(f,i):
  expr = re.compile('^([0-9]+):([0-9]+)$')
  f = expr.search(f)
  i = expr.search(i)
  if (f is None) or (i is None):
    return None
  f = [int(x) for x in f.groups()]
  i = [int(x) for x in i.groups()]
  tm = list(time.localtime())
  tm[5] = 0
  tm[3], tm[4] = f
  tsf = time.mktime(tm)
  tm[3], tm[4] = i
  tsi = time.mktime(tm)  
  if tsi > tsf:
    tsf += 86400.0
  return tsf
    
def doaddpc(req):
  req.default_response()
  validcode = True
  try:
    id,digit = req.form['user'].value.split('-')
    id = int(id)
    if digit != database.gen_usercode(id):
      validcode = False
  except:
    validcode = False
  if validcode:
    user = req.form['user'].value
    cu = database.cx.cursor()
    cu.execute('select name from costumers where id=%d;' % id)
    a = cu.fetchone()
    cu.close()
    if a:
      username = a[0]
      if len(username) > 23:
        tmp = ''
        for x in username.split():
          if len(tmp+x) <= 20:
            tmp += x+' '
        if tmp == '':
          username = username[:20]
        else:
          username = tmp.strip()
        username += '...'
    else:
      validcode = False
  if not validcode:
    username = '-'
    user = ''
  try:
    ts = h2ts(req.form['end'].value, req.form['start'].value)
    if not ts is None:
      if validcode:
        cu.execute('update costumers set total_use=total_use+%d where id=%d;' % (int(round((ts - time.time())/60.0)), id))
        database.cx.commit()
        cu.close()
      cfgloader.do_iptables(req.form['computer'].value, True)
      pcs[req.form['computer'].value] = [
        username,
        req.form['start'].value,
        req.form['end'].value,
        user,
        ts,
      ]
  except:
    pass
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<script language="javascript" type="text/javascript"><!--
window.close();
--></script>
</head>
</html>""")

def change(req):
  id = req.qs['id'][0]
  req.default_response()
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<style type="text/css"><!--
body { font-family:Verdana; }
select { width:200px; border: 1px solid #aaaaaa; color:#444444; }
input { width:120px; border: 1px solid #aaaaaa; color:#444444; background:#f5f5f5; }
input.text { width:200px; border: 1px solid #aaaaaa; color:#444444; background:#ffffff; }
table.panel { background:#eeeeee; width:100%%; border-style:solid; border-width:1px; padding:5px; border-color:#aaaaaa; }
--></style>
<script language="javascript" type="text/javascript" src="/ajax/js"></script>
<script language="javascript" type="text/javascript"><!--
lt='';
req=null;
c=0;
credits=0;
hourprice=%f;
oldend='%s';
function parsehour(s){
  a=s.match(/^([0-9]+):([0-9]+)$/);
  if(a==null)
    return null;
  return parseInt(a[1],10)*60 + parseInt(a[2],10)
}
function diffhour(f,i){
  r=f-i;
  return r;
}
function refdisp(){
  if((f=parsehour(document.getElementById('end').value))==null){
    document.getElementById('end').value='';
    return;
  }
  i=parsehour(oldend);
  document.getElementById('price').value=Math.round((diffhour(f,i)-credits)*hourprice/0.60)/100.0;
}
function onA(){
  if(req.readyState==4&&req.status==200){
    document.getElementById('l').innerHTML=req.responseText;
    credits+=c;
    refdisp();
  }
}
function t(a){
  c=0;
  if(a!=''){
    c=parseInt(a,10);
    a='&d='+a
  }
  req=xmlHTTPAsyncRequest('getuser?id='+document.getElementById('user').value+a,'GET',null,onA);
}
//--></script>
</head>
<body onload="t('')">
<div id="l">
</div><br />
<div align="center">
<form action="dochange" method="post">
<input type="hidden" name="id" value="%s" />
<input type="hidden" id="user" value="%s" />
<table>
<tr><td>%s:</td><td><select name="computer">
<option value="%s" select="select">%s</option>
""" % (cfgloader.cfg['hourprice'], pcs[id][2], id, pcs[id][3], gettext('Computer'), id, id))
  for x in cfgloader.cfg['ips']:
    if not pcs.has_key(x):
      req.wfile.write("""<option value="%s">%s</option>
""" % (x, x))
  req.wfile.write("""</select></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" name="end" id="end" onchange="refdisp()" value="%s" /></td></tr>
<tr><td>%s:</td><td><input type="text" class="text" id="price" /></td></tr>
</table><br />
<input type="submit" name="change" value="%s" />
<input type="submit" name="shutdown" value="%s" />
<input type="submit" name="finish" value="%s" />
</form>
</div>
</body>
</html>
""" % (gettext('End'), pcs[id][2], gettext('Price'), gettext('Change'), gettext('Shutdown'), gettext('Finish')))

def dochange(req):
  id = req.form['id'].value
  if req.form.has_key('change'):
    newid = req.form['computer'].value
    if newid != id:
      pcs[newid] = pcs[id]
      pcs.pop(id)
      id = newid
    pcs[id][2] = req.form['end'].value
    pcs[id][4] = h2ts(pcs[id][2], pcs[id][1])
  else:
    credit = round((pcs[id][4] - time.time())/60.0)
    try:
      userid = int(pcs[id][3].split('-')[0])
    except:
      pass
    else:
      if credit > 0:
        cu = database.cx.cursor()
        cu.execute('update costumers set credit=credit+%d,total_use=total_use-%d where id=%d;' % (credit, credit, userid))
        database.cx.commit()
        cu.close()
    pcs.pop(id)
    if req.form.has_key('shutdown'):
      pckiller.kill(id)
    else:
      cfgloader.do_iptables(id, False)
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<script language="javascript" type="text/javascript"><!--
window.close();
--></script>
</head>
</html>""")
