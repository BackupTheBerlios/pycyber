import socket
import time
from gettext import gettext

import deathcheck
import cfgloader
import config

deathalerts = {}

def kill(id):
  ip = cfgloader.cfg['ips'][id]
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    sock.connect((ip, config.shutdownport))
    data = sock.recv(1024)
    sock.sendall(data)
    sock.close()
  except:
    import main
    main.addalert(gettext("Couldn't send shutdown command to <b>%s</b>. Please check if the computer is on and if the network cable is correctly plugged.") % id)
  cfgloader.do_iptables(id, False)
  deathcheck.add(ip, id)

def dispatch():
  try:
    import main
  except:
    return
  ts = time.time()
  rm = []
  for x in main.pcs:
    if main.pcs[x][4] <= ts:
      rm.append(x)
      kill(x)
  for x in rm:
    main.pcs.pop(x)
  rm = []
  ts -= config.pong_deathtime
  for x in deathcheck.deathlist:
    if deathcheck.deathlist[x][1] < ts:
      if deathcheck.deathlist[x][2] < ts:
        rm.append(x)
        if deathalerts.has_key(x):
          try:
            main.alerts.pop(deathalerts[x])
          except:
            pass
          deathalerts.pop(x)
    else:
      if deathalerts.has_key(x):
        if not main.alerts.has_key(deathalerts[x]):
          rm.append(x)
      else:
        deathalerts[x] = main.addalert(gettext('Shutdown of <b>%s</b> was requested since <b>%s</b>, but it is still on. Please turn it off manually.') % (
          deathcheck.deathlist[x][3],
          time.strftime('%H:%M', time.localtime(deathcheck.deathlist[x][2]))
        ))
  for x in rm:
    deathcheck.deathlist.pop(x)
  deathcheck.send()
