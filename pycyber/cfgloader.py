import cPickle
import config
import os

iptables = {}

try:
  f = file(config.config_dir+'/config.cfg')
  cfg = cPickle.loads(f.read())
  f.close()
except:
  cfg = { 'ips':{}, 'hourprice':0.0 }
    
os.system('iptables -t filter -F pycyber')
    
ips = cfg['ips']
for x in ips:
  os.system('iptables -t filter -A pycyber -s %s -p ! icmp -j DROP' % ips[x])
  iptables[x] = False

def save():
  
  f = file(config.config_dir+'/config.cfg', 'w')
  f.write(cPickle.dumps(cfg))
  f.close()
  
  ips = cfg['ips']
  
  for x in ips:
    if not iptables.has_key(x):
      os.system('iptables -t filter -A pycyber -s %s -p ! icmp -j DROP' % ips[x])
      iptables[x] = False

def do_iptables(id, value):
  if iptables[id] == value:
    return
  iptables[id] = value
  if value:
    os.system('iptables -t filter -D pycyber -s %s -p ! icmp -j DROP' % cfg['ips'][id])
  else:
    os.system('iptables -t filter -A pycyber -s %s -p ! icmp -j DROP' % cfg['ips'][id])
