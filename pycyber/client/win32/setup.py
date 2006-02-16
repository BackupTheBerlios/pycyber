import sys
import re

if len(sys.argv) != 3:
  print 'usage: %s Shutdown-Port Server-IP' % sys.argv[0]

f = file('pycyclient.exe', 'rb')
data = f.read()
f.close()

def change_conf(name, maxval, val):
  global data
  if len(val) > maxval:
    print "%s can't exceed the lenght of %d characters." % (name, maxval)
    sys.exit(1)
  data = re.compile('%s: .{%d}' % (name, maxval)).sub('%s: %s' % (name, val.ljust(maxval, chr(0))), data, 1)

change_conf('Shutdown-Port', 5, sys.argv[1])
change_conf('Server-IP', 15, sys.argv[2])

f = file('pycyclient.exe', 'wb')
f.write(data)
f.close()

print 'The configuration was successfuly updated.'
