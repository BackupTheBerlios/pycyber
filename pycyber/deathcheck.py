import icmp, ip
import socket
import os
import time

pid = os.getpid()
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
sock.setblocking(0)
sock.settimeout(1.0)

deathlist = {}
maxid = 0

def add(dest, desc):
  global maxid
  id = maxid
  deathlist[id] = [dest, 0, time.time(), desc]
  maxid += 1
  if maxid > 500:
    maxid = 0
  return id

def send():
  for id in deathlist:
    pkt = icmp.Packet()
    pkt.type = icmp.ICMP_ECHO
    pkt.id = pid
    pkt.seq = id
    pkt.data = 'death check'
    buf = pkt.assemble()
    try:
      sock.sendto(buf, (deathlist[id][0], 0))
    except:
      pass

def recv():
  try:
    pkt, who = sock.recvfrom(4096)
  except:
    pass
  repip = ip.Packet(pkt)
  reply = icmp.Packet(repip.data)
  if reply.id == pid:
    try:
      deathlist[reply.seq][1] = time.time()
    except:
      pass

