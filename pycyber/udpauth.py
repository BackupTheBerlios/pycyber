import socket
import config

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.settimeout(1.0)

sock.bind((config.ip, config.udpport))

def recv():
  data, addr = sock.recvfrom(1024)
  try:
    import cfgloader
    import main
  except:
    return
  ip = addr[0]
  ips = cfgloader.cfg['ips']
  for x in main.pcs:
    if ips[x] == ip:
      sock.sendto('1', addr)
      break
