import sqlite3
import os

class Database():
	
	def __init__(self, filepath, table_name):
		FilePath_Exists = os.path.exists(filepath)
		self.filepath = filepath
		self.conn = sqlite3.connect(self.filepath)
		self.cur = self.conn.cursor()
		
		self.ColDict = {"Instrument_SN_date_time_Analyte_Name": ["Instrument_SN_date_time", 0],
						"date_time": ["date_time", 0],
						"file_name": ["file_name", 0],
						"conc_lvl": ["conc_lvl", 0],
						"analysis_stage": ["analysis_stage", 0],
						"det_voltage": ["det_voltage", 0],
						"Instrument_SN": ["Instrument_SN", 0],
						"Day": ["Day", 0],
						"Name": ["Name", 0],
						"Area": ["Area", 0],
						"Similarity": ["Similarity", 0],
						"RT": ["R.T. (s)", 0],
						"Height": ["Height", 0],
						"FWHH": ["FWHH (s)", 0],
						"Tailing_Factor": ["Tailing Factor", 0],
						"Peak_SN": ["Peak S/N", 0],
						"Quant_SN": ["Quant S/N", 0],
						"Grp": ["Group", 0]
						}
		
		if not(FilePath_Exists):
			
			statement = '''
				CREATE TABLE %s(
				Instrument_SN_date_time_Analyte_Name TEXT PRIMARY KEY,
				date_time TEXT,
				file_name TEXT,
				conc_lvl TEXT,
				analysis_stage TEXT,
				det_voltage TEXT,
				Instrument_SN TEXT,
				Day TEXT,
				Name TEXT,
				Area TEXT,
				Similarity TEXT,
				RT TEXT,
				Height TEXT,
				FWHH TEXT,
				Tailing_Factor TEXT,
				Peak_SN TEXT,
				Quant_SN TEXT,
				Grp TEXT)
				''' % table_name
			#print statement
			self.conn.execute(statement)
	
	def Get_Columns(self, table):
		#returns a tuple list with all the column names from a given db connection
		column_query = self.conn.execute('SELECT * from %s' % table)
		return [description[0] for description in column_query.description]
	
	def Insert_Query_No_Conditions(self, table, columns, values):
		self.conn.execute("INSERT INTO %s %s VALUES %s" % (table, tuple(columns), tuple(values)))
		self.conn.commit()
		
	def Update_Query(self, table, columns, values, condition):
		query_statement = "UPDATE %s" % table
		
		#create SET portion of query statement including column = value pairs
		col_val = " SET"
		for index, column in enumerate(columns):
			col_val += " %s = '%s'," % (column, values[index])
		col_val = col_val[:-1]
		
		#Define condition
		cond = " WHERE %s" % condition
		
		query_statement += col_val + cond
		
		#print query_statement
		
		self.conn.execute(query_statement)
		self.conn.commit()
			
			
	
	def Select_Query(self, keyword, table, columns, condition, sort):
	
		if keyword == None:
			query_statement = "SELECT"
		else:
			query_statement = "SELECT %s" % keyword
		
		#create columns portion of query statement (column1, column2,...)
		col = ""
		for column in columns:
			col += " %s," % column
		col = col[:-1]
		
		query_statement += "%s FROM %s" % (col, table)
		
		if condition != None:
			query_statement += " WHERE %s" % condition

		if sort != None:
			query_statement += " ORDER BY %s" % sort
		
		# print 'query_statement', query_statement
		
		
		cursor = self.conn.execute(query_statement)
		query_lst = cursor.fetchall()
		
		#print 'query_lst: ', query_lst
		#print 
		
		# if query_lst == []:
			# Null_Query = True
		# else:
			# Null_Query = False
			
		return query_lst
		
	def Delete_Query(self, table, condition):
		
		query_statement = "DELETE FROM %s" % table
		
		if condition != None:
			query_statement += " WHERE %s" % condition
			
		self.conn.execute(query_statement)
		self.conn.commit()
		
		
	
