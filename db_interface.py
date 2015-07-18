import random
import time
from pymongo import MongoClient

c = MongoClient('localhost', 27017)
db = c['atmos_final']

def randKey(digits):
	return ''.join(random.choice(
		'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(digits))

def createTable(ownerproject, tablename):
	if "-" in tablename:
		print("The tablename cannot contain the character '-'.")
		return

	projects = db['projects']
	projectfile = projects.find_one({"name" : ownerproject})
	if projectfile is not None:
		name = ownerproject + "-" + tablename
		if name not in db.collection_names():
			db.create_collection(name)
			description = {"type:" : "description",
						   "duplicate_loss" : 0,
						   "invalid_api_key" : 0,
						   "server_error" : 0,
						   "misc_error" : 0
						  }
			col = db[name]
			col.insert_one(description)

			tablelist = projectfile['tables']
			updatedtablelist = tablelist.append(tablename)
			#In the project description, add this table
			projects.update({'name' : 'ownerproject'}, {"$set" : {"tables" : updatedtablelist}}, upsert=False)
		else:
			print("Error: Table name in this project already exists. Choose a different name.")
	else:
		print("Error: Owner proejct does not exist")

#Access setting: Either public or private
def createProject(name, creator, access):
	projects = db['projects']
	key = randKey(20)
	while(projects.find_one({"secret_key" : key})) is not None:
		key = randKey(20)

	if projects.find_one({"name" : name}) is None:
		description = {"name" : name,
					   "tables" : [name + '-log'],
					   "admins" : [creator],
					   "contributors" : [creator],
					   "readers" : [creator],
					   "access" : access,
					   "secret_key" : key}
		projects.insert_one(description)
	else:
		print("Error: Project name already exists. Choose a different name.")

def log(project, table, value):
	name = project + "-" + table
	if db[name] is not None:
		log = {"type" : "log",
			   "value" : value,
			   "datetime" : int(time.time())}
		db[name].insert_one(log)
	else:
		print('Cannot log because project or table name is not valid.')