from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import select
import imp
import sys
import os
import cgi
import base64
import md5
import time
import gettext

import config
import deathcheck
import udpauth
import pckiller

gettext.bindtextdomain('pycyber', 'lang')
gettext.textdomain('pycyber')

auth_last_try = { }

def module_mtime(module):
  mtime = 0
  if module.__dict__.has_key("__file__"):
    filepath = module.__file__
    try:
      if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        if os.path.exists(filepath[:-1]):
          mtime = max(mtime, os.path.getmtime(filepath[:-1]))
    except OSError: pass
  return mtime

def find_module(module_name, subdir):
  if sys.modules.has_key(module_name):
    module = sys.modules[module_name]
    file = module.__dict__.get('__file__')
    if (not file) or (not file.split('/')[-2] == subdir):
      mtime, oldmtime = 0, -1
    else:
      oldmtime = module.__dict__.get('__mtime__', 0)
      mtime = module_mtime(module)
  else:
    mtime, oldmtime = 0, -1
  if mtime > oldmtime:
    f = False
    try:
      f, p, d = imp.find_module(subdir+'/'+module_name)
      module = imp.load_module(module_name, f, p, d)
    except:
      if f: f.close()
      return None
    if f: f.close()
    if mtime == 0:
      mtime = module_mtime(module)
    module.__mtime__ = mtime
  return module

def md5sum(s):
  dig = md5.md5(s)
  r = ''
  for x in dig.digest():
    r += '%02x' % ord(x)
  return r

class RequestHandler(BaseHTTPRequestHandler):
  
  server_version = 'PyCyber/20060207'
  
  def find_func(self):
    try:
      path = self.path.split('/')
      module_name = path[1]
      func = path[2].split('?')[0]
      module = find_module(module_name, 'htmods')
      if module is None:
        self.send_error(404, 'File not found')
        return None
      if hasattr(module, func):
        return getattr(module, func)
    except:
      pass
    self.send_error(404, 'File not found')
    return None
  
  def parse_qs(self):
    i = self.path.find('?')
    if i >= 0:
      return cgi.parse_qs(self.path[i+1:])
    else:
      return {}

  def send_401(self):
    self.send_response(401)
    self.send_header('WWW-Authenticate', 'Basic realm="pycyber"')
    self.end_headers()
    self.wfile.write('<html><head><title>401 Unauthorized</title></head><body><h1>401 Unauthorized</h1><body></html>')
    return False
  
  def check_auth(self):
    auth = self.headers.getheader('authorization')
    if auth:
      ip = self.client_address[0]
      if auth_last_try.has_key(ip):
        if time.time() - auth_last_try[ip] <= config.auth_delay:
          return self.send_401()
      try:
        auth = base64.decodestring(auth.split()[1])
        user, passwd = auth.split(':')
      except:
        user, passwd = '', ''
      if user != config.user or md5sum(passwd) != config.passwd:
        auth_last_try[ip] = time.time()
        return self.send_401()
      return True
    return self.send_401()

  def do_GET(self):
    if not self.check_auth():
      return
    if self.path == '/':
      self.send_response(301)
      self.send_header('Location', '/main/index')
      self.end_headers()
      self.wfile.write('<html><head><title>301 Moved Permanently</title></head><body><h1>301 Moved Permanently</h1><body></html>')
      return
    func = self.find_func()
    if func is None:
      return
    self.qs = self.parse_qs()
    func(self)
    
  def do_POST(self):
    if not self.check_auth():
      return
    func = self.find_func()
    if func is None:
      return
    env = {'REQUEST_METHOD':'POST'}
    if self.headers.typeheader is None:
      env['CONTENT_TYPE'] = self.headers.type
    else:
      env['CONTENT_TYPE'] = self.headers.typeheader
    length = self.headers.getheader('content-length')
    if length:
      env['CONTENT_LENGTH'] = length
    self.form = cgi.FieldStorage(fp=self.rfile, environ=env)
    self.qs = self.parse_qs()
    func(self)
    
  def default_response(self):
    self.send_response(200)
    self.send_header("Content-Type", "text/html; charset: utf-8")
    self.send_header('Connection', 'close')
    self.end_headers()

class TimeoutedHTTPServer(HTTPServer):
  def get_request(self):
    sock, addr = self.socket.accept()
    sock.settimeout(config.connect_timeout)
    return (sock, addr)

server = TimeoutedHTTPServer((config.ip, config.port), RequestHandler)
fd = server.fileno()

dfd = deathcheck.sock.fileno()
ufd = udpauth.sock.fileno()

while True:
  
  fds = select.select([fd, dfd, ufd], [], [], config.select_timeout)
  
  if fd in fds[0]:
    pckiller.dispatch()
    server.handle_request()
  elif dfd in fds[0]:
    deathcheck.recv()
  elif ufd in fds[0]:
    udpauth.recv()
  else:
    pckiller.dispatch()
