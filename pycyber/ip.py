# Copyright 1997, Corporation for National Research Initiatives
# written by Jeremy Hylton, jeremy@cnri.reston.va.us

import inet
import struct
import string

IPVERSION = 4

class Packet:
  
  def __init__(self, packet):
    self.__disassemble(packet)

  def __unparse_addrs(self):
    src = struct.unpack('cccc', self.src)
    self.src = string.joinfields(map(lambda x:str(ord(x)), src), '.')
    dst = struct.unpack('cccc', self.dst)
    self.dst = string.joinfields(map(lambda x:str(ord(x)), dst), '.')

  def __disassemble(self, raw_packet):
    # The kernel computes the checksum, even on a raw packet. 
    packet = inet.net2iph(raw_packet)
    b1 = ord(packet[0])
    self.v = (b1 >> 4) & 0x0f
    self.hl = b1 & 0x0f
    if self.v != IPVERSION:
      raise ValueError, "cannot handle IPv%d packets" % self.v
    hl = self.hl * 4

    # unpack the fields
    elts = struct.unpack('cchhhcc', packet[:hl-10])
    # struct didn't do !<> when this was written
    self.tos = ord(elts[1]) 
    self.len = elts[2] & 0xffff
    self.id = elts[3] & 0xffff
    self.off = elts[4] & 0xffff
    self.ttl = ord(elts[5])
    self.p = ord(elts[6])
    self.data = packet[hl:]
    self.src = packet[hl-8:hl-4]
    self.dst = packet[hl-4:hl]
    self.__unparse_addrs()
