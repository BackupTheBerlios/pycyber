import re, sys

l = sys.stdin.readlines()
e = re.compile('gettext\(([^)]+)\)')

c={}
for x in l:
  m = e.search(x)
  while m:
    c[eval(m.groups()[0]).replace('"', '\\"')] = 1
    m = e.search(x, m.end())

for x in c:
  print 'msgid "'+x+'"\nmsgstr ""\n'