import atmoslog1_1
import unittest
import time
import random
import sys
import cPickle

testkey = "JRDbEtI00IXRI2D8skcb"
boguskey = "12345678901234567890"
overdrawnkey = "jVPuGnChgeGbfuJpVUOX"
stoppedkey = "AXgVZIYBBBgWLntpSCAA"
wrongcharacterkey = "1234567890123456789$"
fewcharacterkey = "12345678901234567890toomany"

class TestAtmosAPI(unittest.TestCase):
	def setUp(self):
		self.logger = atmoslog1_1.Logger(testkey)

	def tearDown(self):
		pass

	def test_status(self):
		self.assertEqual(self.logger.getStatus(), "go")

	def test_status_wrong_api_key(self):
		self.logger.apikey = boguskey
		with self.assertRaises(atmoslog1_1.ApiKeyDoesNotExistError):
			self.logger.getStatus()
		self.logger.apikey = testkey

	def test_status_overdrawn(self):
		self.logger.apikey = overdrawnkey
		self.assertEqual(self.logger.getStatus(), "WARNING: Further logs will not be committed unless funds are added.")
		self.logger.apikey = testkey

	def test_status_stopped(self):
		self.logger.apikey = stoppedkey
		self.assertEqual(self.logger.getStatus(), "WARNING: Further logs will not be committed unless the project is restarted.")
		self.logger.apikey = testkey

	def test_status_404_character(self):
		self.logger.apikey = wrongcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.getStatus()
		try:
			self.logger.getStatus()
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Only uppercase/lowercase letters and numbers exist in the api key.')
		self.logger.apikey = testkey

	def test_status_404_wrongsize(self):
		self.logger.apikey = fewcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.getStatus()
		try:
			self.logger.getStatus()
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Maximum length of the api key is 20 characters.')
		self.logger.apikey = testkey

	def test_createtable(self):
		self.logger.createTable(''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(10)))
		self.assertEqual(self.logger.recentPrint, "table created")

	def test_createtable_wrong_api_key(self):
		self.logger.apikey = boguskey
		with self.assertRaises(atmoslog1_1.ApiKeyDoesNotExistError):
			self.logger.createTable(''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(10)))
		self.logger.apikey = testkey

	def test_createtable_already_exists(self):
		self.logger.apikey = testkey
		with self.assertRaises(atmoslog1_1.TableNameTakenError):
			self.logger.createTable('log')

	def test_createtable_404_character(self):
		self.logger.apikey = wrongcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.createTable(''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(10)))
		try:
			self.logger.createTable(''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(10)))
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Only uppercase/lowercase letters and numbers exist in the api key.')
		self.logger.apikey = testkey

	def test_createtable_404_wrongsize(self):
		self.logger.apikey = fewcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.createTable(''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(10)))
		try:
			self.logger.createTable(''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for i in range(10)))
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Maximum length of the api key is 20 characters.')
		self.logger.apikey = testkey

	def test_createtable_404_tablecharacters(self):
		self.logger.apikey = testkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.createTable("$$$$$$$")
		try:
			self.logger.createTable("$$$$$$$")
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Only alphanumeric characters and underscores can be included in the table name.')
		self.logger.apikey = testkey

	def test_createtable_404_maxtablecharactersize(self):
		self.logger.apikey = testkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.createTable("012345678901234567890123456789012345678901234567890")
		try:
			self.logger.createTable("012345678901234567890123456789012345678901234567890")
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Maximum length of the table name is 50 characters.')
		self.logger.apikey = testkey

	def test_createtable_404_mintablecharactersize(self):
		self.logger.apikey = testkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.createTable("0")
		try:
			self.logger.createTable("0")
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Minimum length of the table name is 3 characters.')
		self.logger.apikey = testkey

	#Methods for logging data

	def test_log(self):
		self.logger.recentPrint = ""
		self.logger.apikey = testkey
		self.logger.log("log", "testlog")
		self.logger.commitLogsIntoDB()
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	def test_log_manualcommit(self):
		self.logger.recentPrint = ""
		self.logger.apikey = testkey
		self.logger.log("log", "testlog")
		self.logger.commit()
		time.sleep(2)
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	def test_log_wrong_api_key(self):
		self.logger.apikey = boguskey
		self.logger.log("log", "testlog")
		with self.assertRaises(atmoslog1_1.ApiKeyDoesNotExistError):
			self.logger.commitLogsIntoDB()
		self.logger.apikey = testkey

	def test_log_wrong_table_name(self):
		self.logger.apikey = testkey
		self.logger.log("atablethatdoesnotexist", "testlog")
		with self.assertRaises(atmoslog1_1.TableDoesNotExistError):
			self.logger.commitLogsIntoDB()

	def test_log_overdrawn_project(self):
		self.logger.recentPrint = ""
		self.logger.apikey = overdrawnkey
		self.logger.log("log", "testlog")
		self.logger.commitLogsIntoDB()
		self.assertEqual(self.logger.recentPrint, "WARNING: Further logs will not be committed unless funds are added.")

	def test_log_stopped_project(self):
		self.logger.recentPrint = ""
		self.logger.apikey = stoppedkey
		self.logger.log("log", "testlog")
		self.logger.commitLogsIntoDB()
		self.assertEqual(self.logger.recentPrint, "WARNING: Further logs will not be committed unless the project is restarted.")

	def test_log_404_character(self):
		self.logger.apikey = wrongcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.log("log", "testlog")
			self.logger.commitLogsIntoDB()
		try:
			self.logger.log("log", "testlog")
			self.logger.commitLogsIntoDB()
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Only uppercase/lowercase letters and numbers exist in the api key.')
		self.logger.apikey = testkey

	def test_log_404_wrongsize(self):
		self.logger.apikey = fewcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.log("log", "testlog")
			self.logger.commitLogsIntoDB()
		try:
			self.logger.log("log", "testlog")
			self.logger.commitLogsIntoDB()
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Maximum length of the api key is 20 characters.')
		self.logger.apikey = testkey

	def test_log_auto_cache(self):
		self.logger.apikey = testkey
		self.logger.max_cache_size = 1000
		self.logger.recentPrint = ""
		while self.logger.status != "writing":
			self.logger.log("log", ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5)))
		time.sleep(2)
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	def test_second_cache(self):
		self.logger.apikey = testkey
		self.logger.max_cache_size = 1000
		self.logger.status = "writing"
		self.logger.recentPrint = ""
		self.logger.log("log", ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5)))
		self.logger.status = "open"
		while self.logger.status != "writing":
			self.logger.log("log", ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5)))

		time.sleep(2)
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	#Methods for bulk-logging data

	def test_bulk_log(self):
		self.logger.recentPrint = ""
		self.logger.apikey = testkey
		self.logger.bulkLog("log", ["testlog", "testlog2"])
		self.logger.commitLogsIntoDB()
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	def test_bulk_log_manualcommit(self):
		self.logger.recentPrint = ""
		self.logger.apikey = testkey
		self.logger.bulkLog("log", ["testlog", "testlog2"])
		self.logger.commit()
		time.sleep(2)
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	def test_bulk_log_wrong_api_key(self):
		self.logger.apikey = boguskey
		self.logger.bulkLog("log", ["testlog", "testlog2"])
		with self.assertRaises(atmoslog1_1.ApiKeyDoesNotExistError):
			self.logger.commitLogsIntoDB()
		self.logger.apikey = testkey

	def test_bulk_log_wrong_table_name(self):
		self.logger.apikey = testkey
		self.logger.log("atablethatdoesnotexist", ["testlog", "testlog2"])
		with self.assertRaises(atmoslog1_1.TableDoesNotExistError):
			self.logger.commitLogsIntoDB()

	def test_bulk_log_overdrawn_project(self):
		self.logger.recentPrint = ""
		self.logger.apikey = overdrawnkey
		self.logger.bulkLog("log", ["testlog", "testlog2"])
		self.logger.commitLogsIntoDB()
		self.assertEqual(self.logger.recentPrint, "WARNING: Further logs will not be committed unless funds are added.")

	def test_bulk_log_stopped_project(self):
		self.logger.recentPrint = ""
		self.logger.apikey = stoppedkey
		self.logger.bulkLog("log", ["testlog", "testlog2"])
		self.logger.commitLogsIntoDB()
		self.assertEqual(self.logger.recentPrint, "WARNING: Further logs will not be committed unless the project is restarted.")

	def test_bulk_log_404_character(self):
		self.logger.apikey = wrongcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.bulkLog("log", ["testlog", "testlog2"])
			self.logger.commitLogsIntoDB()
		try:
			self.logger.bulkLog("log", ["testlog", "testlog2"])
			self.logger.commitLogsIntoDB()
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Only uppercase/lowercase letters and numbers exist in the api key.')
		self.logger.apikey = testkey

	def test_bulk_log_404_wrongsize(self):
		self.logger.apikey = fewcharacterkey
		with self.assertRaises(atmoslog1_1.Atmos404Error):
			self.logger.bulkLog("log", ["testlog", "testlog2"])
			self.logger.commitLogsIntoDB()
		try:
			self.logger.bulkLog("log", ["testlog", "testlog2"])
			self.logger.commitLogsIntoDB()
		except atmoslog1_1.Atmos404Error as e:
			self.assertEqual(e.msg, 'Maximum length of the api key is 20 characters.')
		self.logger.apikey = testkey

	def test_bulk_log_auto_cache(self):
		self.logger.apikey = testkey
		self.logger.max_cache_size = 1000
		self.logger.recentPrint = ""
		while self.logger.status != "writing":
			self.logger.bulkLog("log", [''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5)), ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5))])
		time.sleep(2)
		self.assertEqual(self.logger.recentPrint, "logged successfully")

	def test_bulk_log_second_cache(self):
		self.logger.apikey = testkey
		self.logger.max_cache_size = 1000
		self.logger.status = "writing"
		self.logger.recentPrint = ""
		self.logger.bulkLog("log", [''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5)), ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5))])
		self.logger.status = "open"
		while self.logger.status != "writing":
			self.logger.bulkLog("log", [''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5)), ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_') for i in range(5))])
		time.sleep(2)
		self.assertEqual(self.logger.recentPrint, "logged successfully")	

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestAtmosAPI)
	unittest.TextTestRunner(verbosity=2).run(suite)