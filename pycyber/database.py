import pysqlite2.dbapi2 as sqlite
import os
import base64
import md5

import config

path = config.config_dir+'/database.db'
if not os.path.exists(path):
  cx = sqlite.connect(path)
  cu = cx.cursor()
  cu.execute('create table costumers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, birthday TEXT, address TEXT, telephone TEXT, credit INTEGER, total_use INTEGER);')
  cu.close()
  cx.commit()
else:
  cx = sqlite.connect(path)

def gen_usercode(id):
  s = base64.b64encode(str(int(id)))
  s = base64.b64encode(md5.md5('passone'+s+config.usercode_key).digest())
  s = base64.b64encode(md5.md5(config.usercode_key+s+'passtwo').digest())
  s = s.replace('+', '0')
  s = s.replace('/', '1')
  return (s[ord(s[0]) % 22] + s[ord(s[1]) % 22]).lower()
