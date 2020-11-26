from flask import Flask, request
import requests
import json
from Database import database
import logging
import time

app = Flask(__name__)
logging.basicConfig(filename="log.txt", level=logging.INFO)


@app.route("/add", methods=['POST'])
def add():
	try:
		try:
			r = json.loads(request.data)  # преобразование json запроса
		except Exception as e:
			logging.error(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition"}

		# проверка dictionary name
		if 'dictionary name' not in r:
			logging.error(time.ctime(time.time()) + " json recognition - json is not full - dictionary name")
			return {"status": "error", "type error": "json recognition"}
		if not r['dictionary name'].isalpha():
			logging.error(time.ctime(time.time()) + " dictionary name - forbidden symbols")
			return {"status": "error", "type error": "dictionary names"}
		if r['dictionary name'] not in database:
			logging.error(time.ctime(time.time()) + " dictionary name - dictionary does not exist")
			return {"status": "error", "type error": "dictionary name"}

		# проверка значений
		if 'amount of elements' not in r:
			logging.error(time.ctime(time.time()) + " json recognition - json is not full - amount of elements")
			return {"status": "error", "type error": "json recognition"}
		if type(r['amount of elements']) != int:
			logging.error(time.ctime(time.time()) + " amount of elements - not a number")
			return {"status": "error", "type error": "amount of elements"}
		if 'values' not in r:
			logging.error(time.ctime(time.time()) + " json recognition - json is not full - values")
			return {"status": "error", "type error": "json recognition"}
		if type(r['values']) != dict:
			logging.error(time.ctime(time.time()) + " values - not a dict")
			return {"status": "error", "type error": "values"}

		# Приравнивание
		database[r['dictionary name']] = {**database[r['dictionary name']], **r['values']}

		# Сообщить другим серверам

		# Вывод
		return {"status": "done", "dictionary name": r['dictionary name'],
				"updated dictionary": database[r['dictionary name']]}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + str(e))
		return {"status": "error", "type error": "unknown error"}


@app.route("/databases", methods=['GET'])
def data():
	return {**database}


@app.route("/delete", methods=['POST'])
def delete():
	try:
		try:
			r = json.loads(request.data)  # преобразование json запроса
		except:
			logging.error(time.ctime(time.time()) + " json recognition - not json")
			return {"status": "error", "type error": "json recognition"}

		# проверка dictionary name
		if 'dictionary name' not in r:
			logging.error(time.ctime(time.time()) + " json recognition - json is not full - dictionary name")
			return {"status": "error", "type error": "json recognition"}
		if not r['dictionary name'].isalpha():
			logging.error(time.ctime(time.time()) + " dictionary name - forbidden symbols")
			return {"status": "error", "type error": "dictionary names"}
		if r['dictionary name'] not in database:
			logging.error(time.ctime(time.time()) + " dictionary name - dictionary does not exist")
			return {"status": "error", "type error": "dictionary name"}

		# проверка key
		if r['key'] not in database[r['dictionary name']]:
			logging.error(time.ctime(time.time()) + " key - key does not exist")
			return {"status": "error", "type error": "key"}

		# удаление
		del database[r['dictionary name']][r['key']]

		return {"status": "done", "dictionary name": r['dictionary name'],
				"updated dictionary": database[r['dictionary name']]}
	except Exception as e:
		logging.error(time.ctime(time.time()) + " " + str(e))
		return {"status": "error", "type error": "unknown error"}


if __name__ == '__main__':
	app.run()
