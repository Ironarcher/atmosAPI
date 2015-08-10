import urllib2
import json
import sys
import thread
import re
import cPickle

#Exception definitions
class Atmos404Error(Exception):
	#Maximum length is 50 characters
	def __init__(self, apikey, tablename):
		self.msg= "Atmos 404 Error"
		if tablename is not None:
			if re.match('^\w+$', tablename) is None:
				self.msg = 'Only alphanumeric characters and underscores can be included in the table name.'
			elif len(tablename) > 50:
				self.msg = 'Maximum length of the table name is 50 characters.'
			elif len(tablename) < 3:
				self.msg = 'Minimum length of the table name is 3 characters.'
		if apikey is not None and self.msg == "Atmos 404 Error":
			if re.match("^[A-Za-z0-9]*$", apikey) is None:
				self.msg = 'Only uppercase/lowercase letters and numbers exist in the api key.'
			elif len(apikey) > 20:
				self.msg = 'Maximum length of the api key is 20 characters.'

class TableDoesNotExistError(Exception):
	def __init__(self, value):
		self.msg = "The table " + value + " does not exist in this project."

class ApiKeyDoesNotExistError(Exception):
	def __init__(self, value):
		self.msg = "The apikey " + value + " does not exist."

class TableNameTakenError(Exception):
	def __init__(self, value):
		self.msg = "The table name " + value + " has already been created in your project"

class Logger:
	url_base = "http://127.0.0.1:8000"

	def __init__(self, apikeyinit):
		self.apikey = apikeyinit
		self.status = "open"
		self.cache = {}
		self.second_cache = {}
		#Default maximum cache size is ~10kb
		self.max_cache_size = 10000
		self.recentPrint = "logger started"
		print(self.getStatus())

	def log(self, tablename, log_content):
		if self.status == "writing":
			#Append the log and table to the cache
			if tablename not in self.second_cache:
				self.second_cache[tablename] = [log_content]
			else:
				self.second_cache[tablename].append(log_content)
		elif self.status == "open":
			#Dump the second_cache into the first cache if the focus transitions:
			if len(self.second_cache) > 0:
				self.cache = self.second_cache
				self.second_cache = {}

			#Append the log and table to the cache
			if tablename not in self.cache:
				self.cache[tablename] = [log_content]
			else:
				self.cache[tablename].append(log_content)
			#If the cache is full, dump the cache into to Atmos database
			if sys.getsizeof(cPickle.dumps(self.cache)) >= self.max_cache_size:
				self.status = "writing"
				self.commit()

	def commit(self):
		thread.start_new_thread(self.commitLogsIntoDB, ())

	def commitLogsIntoDB(self):
		for table in self.cache.keys():
			search = self.url_base + "/api/bulklog/" + self.apikey + "/" + table + "/"
			for log in self.cache[table]:
				log = urllib2.quote(str(log), safe='')
				search = search + str(log) + "&"
			#remove the last ampersand (too many)
			search = search[:-1]
		try: 
			response = urllib2.urlopen(search)
			data = json.loads(response.read())
			if data['error'] == "incorrect api key":
				raise ApiKeyDoesNotExistError(self.apikey)
			elif data['error'] == "incorrect table name":
				raise TableDoesNotExistError(table)
			elif data['error'] == "project_overdrawn":
				print("WARNING: Further logs will not be committed unless funds are added.")
				self.recentPrint = "WARNING: Further logs will not be committed unless funds are added."
			elif data['error'] == "project_stopped":
				print("WARNING: Further logs will not be committed unless the project is restarted.")
				self.recentPrint = "WARNING: Further logs will not be committed unless the project is restarted."
			elif data['error'] == "logged but failed to charge" or data['error'] == "processing error":
				print("WARNING: Some logs were lost because of server errors")
				self.recentPrint = "WARNING: Somes logs were lost because of server errors" 
			else:
				self.recentPrint = "logged successfully"
		except urllib2.HTTPError:
			raise Atmos404Error(self.apikey, table)

		self.status = "open"
		self.cache = {}

	def getStatus(self):
		search = self.url_base + "/api/status/" + self.apikey + "/"
		try:
			response = urllib2.urlopen(search)
			data = json.loads(response.read())
			if data['error'] == "incorrect api key":
				raise ApiKeyDoesNotExistError(self.apikey)
			elif data['project_status'] == "overdrawn":
				return "WARNING: Further logs will not be committed unless funds are added."
			elif data['project_status'] == "stopped":
				return "WARNING: Further logs will not be committed unless the project is restarted."
			elif data['error'] == "server_error":
				return "WARNING: This request was lost because of a server error."
			elif data['error'] == "" and data['project_status'] == "running" and data['server_status'] == "on":
				self.recentPrint = "status go"
				return "go"
			else:
				return "unknown error"
		except urllib2.HTTPError:
			raise Atmos404Error(self.apikey, None)

	def createTable(self, newtablename):
		search = self.url_base + "/api/createtable/" + self.apikey + "/" + newtablename + "/"
		try:
			response = urllib2.urlopen(search)
			data = json.loads(response.read())
			if data['error'] == "incorrect api key":
				raise ApiKeyDoesNotExistError(self.apikey)
			elif data['error'] == "table name already taken":
				raise TableNameTakenError(newtablename)
			else:
				self.recentPrint = "table created"
		except urllib2.HTTPError:
			raise Atmos404Error(self.apikey, newtablename)

	def bulkLog(self, tablename, multiple_log_content):
		if self.status == "writing":
			#Append the log and table to the cache
			if tablename not in self.second_cache:
				self.second_cache[tablename] = [multiple_log_content[0]]
				multiple_log_content = multiple_log_content[1:]
			for log in multiple_log_content:
				self.second_cache[tablename].append(log)
		elif self.status == "open":
			#Dump the second_cache into the first cache if the focus transitions:
			if len(self.second_cache) > 0:
				self.cache = self.second_cache
				self.second_cache = {}

			#Append the log and table to the cache
			if tablename not in self.cache:
				self.cache[tablename] = [multiple_log_content[0]]
				multiple_log_content = multiple_log_content[1:]
			for log in multiple_log_content:
				self.cache[tablename].append(log)
			#If the cache is full, dump the cache into to Atmos database
			if sys.getsizeof(cPickle.dumps(self.cache)) >= self.max_cache_size:
				self.status = "writing"
				self.commit()