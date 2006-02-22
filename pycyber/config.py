# Ip of the network interface where the servers will listen. Leave it
# blank for listening in all interfaces.
ip = ''

# The port where the admin server will listen.
port = 7777

# The port where the udp auth server will listen.
udpport = 7770

# The port to send shutdown command to the clients.
shutdownport = 7771

# Username and md5 of the password for logging in the admin server.
user = 'user'
passwd = '76a2173be6393254e72ffa4d6df1030a'

# A secret key for generating the user-code verification digits.
usercode_key = 'change this, please!'

# Min delay between auth retrys, in seconds. Avoids brute force.
auth_delay = 5.0

# Timeout for http connections to the server. Avoids DoS attacks.
connect_timeout = 4.0

# Timeout for select calls, in seconds. Affects the delay for calling dispatch
# modules and overall server performance.
select_timeout = 10.5

# Time in seconds without receiving PONG in which a computer will be considered
# dead.
pong_deathtime = 17.0

# Refresh time in seconds. Time for refreshing the main admin server page.
refresh_time = 10

# Writable dir for storing internal config files.
config_dir = '/var/pycyber'

# Directory containing language localization.
locale_dir = '/usr/share/locale'

