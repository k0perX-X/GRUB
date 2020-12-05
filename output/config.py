from hashlib import md5

user_logins = {
	'admin': md5('123456'.encode('utf8')).hexdigest()
}

login = 'server1'
base_cycle_time = 5
multiplier_update_cycle_time = 1000

first = True
start_leader = ''
debug = True
