# Copyright 1997, Corporation for National Research Initiatives
# written by Jeremy Hylton, jeremy@cnri.reston.va.us

import inet
import array
import struct

ICMP_ECHO = 8

class Packet:
  def __init__(self, packet=None, cksum=1):
    if packet:
      self.__disassemble(packet, cksum)
    else:
      self.type = 0
      self.code = 0
      self.cksum = 0
      self.id = 0
      self.seq = 0
      self.data = ''

  def assemble(self, cksum=1):
    idseq = struct.pack('hh', self.id, self.seq)
    packet = chr(self.type) + chr(self.code) + '\000\000' + idseq + self.data
    if cksum:
      self.cksum = inet.cksum(packet)
      packet = chr(self.type) + chr(self.code) + struct.pack('H', self.cksum) + idseq + self.data
    self.__packet = packet
    return self.__packet

  def __disassemble(self, packet, cksum=1):
    if cksum:
      our_cksum = inet.cksum(packet)
      if our_cksum != 0:
        raise ValueError, packet
    self.type = ord(packet[0])
    self.code = ord(packet[1])
    elts = struct.unpack('hhh', packet[2:8])
    [self.cksum, self.id, self.seq] = map(lambda x:x & 0xffff, elts)
    self.data = packet[8:]
