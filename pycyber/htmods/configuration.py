from gettext import gettext

import cfgloader

def index(req):
  req.default_response()
  ipliststr = ''
  ips = cfgloader.cfg['ips']
  for x in ips:
    ipliststr += 'Array(%s, %s),' % (repr(ips[x]), repr(x))
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<style type="text/css"><!--
body { font-family:Verdana; }
select { width:200px; border: 1px solid #aaaaaa; color:#444444; }
input { border: 1px solid #aaaaaa; color:#444444; background:#f5f5f5; }
input.text { width:120px; border: 1px solid #aaaaaa; color:#444444; background:#ffffff; }
--></style>
<script language="javascript" type="text/javascript"><!--
iplist = Array(
%s
);
function ad()
{
  iplist.push(Array('',''));
  m();
}
function r(n)
{
  iplist.splice(n,1);
  m();
}
function a(n,i)
{
  iplist[n][i] = document.getElementById('d'+String(i)+String(n)).value;
}
function m()
{
  html='';
  for(i=0;i<iplist.length;i++)
    html+='ip: <input class="text" type="text" id="d0'+i+'" value="'+iplist[i][0]+'" onchange="a('+i+',0)" /> \
id: <input class="text" type="text" id="d1'+i+'" value="'+iplist[i][1]+'" onchange="a('+i+',1)" /> \
<input type="button" onclick="r('+i+')" value="%s" /><br />';
  document.getElementById('iplist').innerHTML = html;
}
function gendata()
{
  data = '';
  for(i=0;i<iplist.length;i++)
    if(iplist[i][0]!=''&&iplist[i][1]!='')
      data+=iplist[i][0]+'|'+iplist[i][1]+'|';
  document.getElementById('iplistdata').value = data;
}
//--></script>
</head>
<body onload="m()">
<div align="center">
%s
<div id="iplist" align="center">
</div>
<input type="button" onclick="ad()" value="%s" /><br /><br />
<form action="sendcfg" method="post" onsubmit="gendata()">
<input type="hidden" name="iplistdata" id="iplistdata" />
<table>
<tr><td>%s:</td><td><input type="text" class="text" name="hourprice" value="%.3f" /></td></tr>
</table><br />
<input type="submit" value="OK" />
</form>
</div>
</body>
</html>
""" % (ipliststr[:-1], gettext('Remove'), gettext('Computers in the network'), gettext('Add'),
  gettext('Hour price'), cfgloader.cfg['hourprice']))

def sendcfg(req):
  req.default_response()
  a = req.form['iplistdata'].value.split('|')[:-1]
  cfgloader.cfg['ips'].clear()
  for i in range(len(a)/2):
    cfgloader.cfg['ips'][a[i*2+1]] = a[i*2]
  try:
    cfgloader.cfg['hourprice'] = float(req.form['hourprice'].value.replace(',','.'))
  except:
    pass
  cfgloader.save()
  req.wfile.write("""<html>
<head>
<title>pycyber</title>
<script language="javascript" type="text/javascript"><!--
window.close();
--></script>
</head>
</html>""")
