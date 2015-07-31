import urllib2
import json

apikey = ""
url_base = "127.0.0.1:8000"
cache = {
	"log" : []
}

#Default maximum cache size is ~10 mb
max_cache_size = 10000000

def log(tablename, log_content):
	cache[tablename].append(log_content)
	# if cache bytes > max_cache_size:
	# commitLogsIntoDB()

def commitLogsIntoDB():
	for table in cache.keys():
		search = url_base + "/api/bulklog/" + apikey + "/"
		for log in table:
			if "&" in log:
				log.replace("&", "!%><")
			search = search + log + "&"
		#remove the last ampersand (too many)
		response = urllib2.urlopen
		




