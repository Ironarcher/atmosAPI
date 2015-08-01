import urllib2
import json
import sys
import thread

#Exception definitions
class WrongAPIKeyError(Exception):
	def _init__(self, value):
		self.value = "The API key " + value + " was not valid."
	def __str__(self):
		return repr(self.value)

class WrongTableError(Exception):
	def _init__(self, value):
		self.value = "The table " + value + " does not exist in this project."
	def __str__(self):
		return repr(self.value)

class Logger:
	url_base = "http://127.0.0.1:8000"

	def __init__(self, apikeyinit):
		self.apikey = apikeyinit
		self.status = "open"
		self.cache = {}
		self.second_cache = {}
		#Default maximum cache size is ~10mb
		self.max_cache_size = 10000000

	def log(self, tablename, log_content):
		if self.status == "writing":
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
			if sys.getsizeof(self.cache) > self.max_cache_size:
				self.status = "writing"
				self.commit()

	def commit(self):
		thread.start_new_thread(self.commitLogsIntoDB, ())

	def commitLogsIntoDB(self):
		for table in self.cache.keys():
			search = self.url_base + "/api/bulklog/" + self.apikey + "/" + table + "/"
			for log in self.cache[table]:
				log = urllib2.quote(log, safe='')
				search = search + log + "&"
			#remove the last ampersand (too many)
			search = search[:-1]
			print(search)
			response = urllib2.urlopen(search)
			try: 
				data = json.loads(response.read())
				if data['error'] == "incorrect api key":
					raise WrongAPIKeyError(apikey)
				elif data['error'] == "incorrect table name":
					raise WrongTableError(table)
				elif data['error'] == "project_overdrawn":
					print("WARNING: Further logs will not be committed unless funds are added.")
				elif data['error'] == "project_stopped":
					print("WARNING: Further logs will not be committed unless the project is restarted.")
				elif data['error'] == "logged but failed to charge" or data['error'] == "processing error":
					print("WARNING: Some logs were lost because of server errors")
			except ValueError:
				print("A 404 error has occured. Check your apikey and table name again.")

		self.status = "open"
		self.cache = {}