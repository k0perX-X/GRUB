from hashlib import md5
# 'username': md5('password'.encode('utf8')).hexdigest()

saved_user_logins = {
	'admin': md5('admin'.encode('utf8')).hexdigest()
}
