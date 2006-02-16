# Copyright 1997, Corporation for National Research Initiatives
# written by Jeremy Hylton, jeremy@cnri.reston.va.us

import array
import struct
from socket import htons, ntohs

def cksum(s):
  if len(s) & 1:
    s = s + '\0'
  words = array.array('H', s)
  sum = 0
  for word in words:
    sum = sum + (word & 0xffff)
  hi = sum >> 16
  lo = sum & 0xffff
  sum = hi + lo
  sum = sum + (sum >> 16)
  return (~sum) & 0xffff

def gets(s):
  return struct.unpack('H', s)[0] & 0xffff

def mks(h):
  return struct.pack('H', h)

def net2iph(s):
  len = ntohs(gets(s[2:4]))
  id = ntohs(gets(s[4:6]))
  off = ntohs(gets(s[6:8]))
  return s[:2] + mks(len) + mks(id) + mks(off) + s[8:]
