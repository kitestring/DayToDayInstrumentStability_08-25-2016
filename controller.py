import wx
import time
from sqliteapi import Database 
from excelwriter import ExcelFile
import sqlite3
from subprocess import call
import datetime
import os
import statistics as s
import math as m

class D2D_Frame(wx.Frame):
	def __init__(self, parent, title):
		frame_width = 550
		frame_height = 410
		wx.Frame.__init__(self, parent, title=title, size=(frame_width,frame_height))
		
		#Bind events
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		
	def OnExit(self, event):
		if os.path.exists(os.path.join(os.getcwd(), 'temp.txt')):
			os.remove(os.path.join(os.getcwd(), 'temp.txt'))
		panel.EventLogger('Saving & Disconnecting from databases.\n\t\tPlease Wait...')
		panel.D2Ddb.conn.close()
		self.Destroy()
		
		
		
class D2D_Panel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		
		#Set excel coordinates values
		self.setdata_startcolumn = 38
		self.setdata_lvl_column_spacer = 12
		self.start_row = 2
		self.summarydata_field_row_spacer = 55
		self.summarydata_cell_coordinates = {'1': {'row': 0, 'col': -9}, '2': {'row': 0, 'col': -5}, 
											'3': {'row': 14, 'col': -9}, '4': {'row': 14, 'col': -5}}
		
		self.graph_metadata = {'1': {'color': '#C0C0C0', 'row': 0, 'col': 1}, '2': {'color': '#00FF00', 'row': 0, 'col': 15}, 
											'3': {'color': '#FFFF00', 'row': 26, 'col': 1}, '4': {'color': '#00FFFF', 'row': 26, 'col': 15}}
		
		
		#Connect to database
		fp = os.path.join(os.getcwd(), "D2D.db")
		self.D2D_Table= 'Analyte_Data'
		self.D2Ddb = Database(fp, self.D2D_Table)
		self.D2Ddb_columns = self.D2Ddb.Get_Columns(self.D2D_Table)
		
	
		#create sizers
		main_VertSizer = wx.BoxSizer(wx.VERTICAL)
		buttons_HorzSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttons_VertSizer = wx.BoxSizer(wx.VERTICAL)
		controls_HorzSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		#create status output text control
		self.lbl_status_logger = wx.StaticText(self, label=" Status Output: ")
		main_VertSizer.Add(self.lbl_status_logger, wx.ALIGN_LEFT)
		self.status_logger = wx.TextCtrl(self, size=(530,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		main_VertSizer.Add(self.status_logger, wx.ALIGN_LEFT)
		
		#create radio buttons
		radioList = ['VP1', 'VP2', 'GS']
		self.instrument_SN_radiobut = wx.RadioBox(self, label="Instrument",  
			choices=radioList, style=wx.RA_SPECIFY_COLS)
		# self.Bind(wx.EVT_RADIOBOX, self.EvtInstrumentSNRadiobut, self.instrument_SN_radiobut)
		
		#create buttons
		self.mine_data_btn = wx.Button(self, label = "Mine Data")
		self.display_data_btn = wx.Button(self, label = "Display Data")
		
		buttons_HorzSizer.Add(self.mine_data_btn, wx.ALIGN_BOTTOM)
		buttons_HorzSizer.Add(self.display_data_btn, wx.ALIGN_BOTTOM)
		buttons_VertSizer.Add((10,25))
		buttons_VertSizer.Add(buttons_HorzSizer)
		controls_HorzSizer.Add(self.instrument_SN_radiobut)
		controls_HorzSizer.Add(buttons_VertSizer)
		
		
		self.Bind(wx.EVT_BUTTON, self.OnMineData, self.mine_data_btn)
		self.Bind(wx.EVT_BUTTON, self.OnDisplayData, self.display_data_btn)
		
	
		main_VertSizer.Add(controls_HorzSizer)
		self.SetSizerAndFit(main_VertSizer)

	
	def OnMineData(self, event):

		self.dirname = ''
		InstSN = str("%s" % self.instrument_SN_radiobut.GetStringSelection())
		
		#Get D2D txt raw data files
		dlg = wx.FileDialog(self, "Select the D2D txt raw data files to import", self.dirname, "", "*.txt", wx.FD_MULTIPLE)
		if dlg.ShowModal() == wx.ID_OK:
		
			#get the txt full paths and file names from dialogue objects
			txt_fullpaths_lst = dlg.GetPaths()
			txt_filenames_lst = dlg.GetFilenames()
			
			#Iterate through each txt file defined
			#and mine analyte data
			for txtfile_index, txt_file in enumerate(txt_fullpaths_lst):
				
				#open text file, find and replace specified strings
				#method returns tempfile which has replaced strings 
				tempfile = self.FindReplaceStringInTextFile(txt_file, {'1st Dimension Time (s)': 'R.T. (s)'})
				
				#dump the tempfile contents into txt_file_contents
				txt_file_contents = open(tempfile, 'r')
				
				#create new ChromatTOF object, set/reset metadatalst, valid file boolean, and headers found
				ct = ChromatTOF()
				metadatalst = []
				valid_txtfile = True
				headers_found = 0
				
				#Iterate through each line of the given file
				for line_index, line in enumerate(txt_file_contents):
					
					#parce the line of text into a list & remove the "\n" from the last list element
					line_parced = line.split("\t")
					line_parced[-1] = line_parced[-1].replace("\n","")
				
					if line_index == 0:
						#reformat input datetime (mm/dd/yyyy hh:mm:ss 12 hour clock) into yyyy-mm-dd hh:mm:ss 24 hour clock
						#then append to metadatalst
						#also append text file name to metadatalst
						
						datetime_parced  =  line_parced[0].split(" ")
						
						try:
							reformatted_date = str(datetime.datetime.strptime(datetime_parced[0], '%m/%d/%Y').strftime('%Y-%m-%d'))
							time_parced = datetime_parced[1].split(":")
							
							#Convert from AM/PM notation to 24 hr clock
							if datetime_parced[2] == "PM" and int(time_parced[0]) < 12:
								time_parced[0] = str(int(time_parced[0]) + 12)
							elif datetime_parced[2] == "AM" and int(time_parced[0]) == 12:
								time_parced[0] = str(int(time_parced[0]) - 12)
							
							#Zero pad the the hour
							if len(time_parced[0]) == 1:
								time_parced[0] = "0" + time_parced[0]
							
							reformatted_time = '%s:%s:%s' % (time_parced[0], time_parced[1], time_parced[2])
							reformatted_datetime = "%s %s" % (reformatted_date, reformatted_time)
							

							#primary key value without the _analyte name appended
							Instrument_SN_date_time_Analyte_Name = "%s%s" % (InstSN, reformatted_datetime)
							metadatalst.append(Instrument_SN_date_time_Analyte_Name)
							metadatalst.append(reformatted_datetime)
							metadatalst.append(str(txt_filenames_lst[txtfile_index]))
						
						except ValueError:
							#This is an imporperly formatted source data file; skip file and move on
							valid_txtfile = False
							break

					elif line_index == 1:
						#append conc_lvl, analysis_stage, & det_voltage to metadatalst
						#then calculte the day number and append to metadatalst
						sample_attributes_parced  =  line_parced[0].split(" ")
						metadatalst.append(sample_attributes_parced[0])
						metadatalst.append(sample_attributes_parced[1])
						metadatalst.append(sample_attributes_parced[2])
						metadatalst.append(InstSN)
						metadatalst.append(self.Determine_Day(reformatted_datetime, InstSN, sample_attributes_parced[0], sample_attributes_parced[1], str(txt_filenames_lst[txtfile_index])))

						
					elif line_index == 2:
						#Find the each header and get the corresponding line_parced index numbers
						for header_index, header in enumerate (line_parced):
						
							if header in ct.ColumnList:
								headers_found += 1
								ct.ColumnIndexDict[header] = header_index

						if headers_found != 10:
							#This is an imporperly formatted source data file; skip file and move on
							valid_txtfile = False
							break
							
					elif line_index >= 3:

						#Find the each analytes line and grab each field corresponding to the headers
						#Also populate the analyte_group variable it the group label in the AnalyteDict data structure
						analyte = line_parced[ct.ColumnIndexDict['Name']]
						Grp = line_parced[ct.ColumnIndexDict['Group']]
						analyte_group = ct.AnalyteDict.get(analyte,[None])

						if analyte in ct.AnalyteLst and Grp == analyte_group[0]:
	
							# now mine the data into the ct.AnalyteDict[analyte][1].append(shit) and set ct.AnalyteDict[analyte][2] = True
							#Define analyte found = True
							ct.AnalyteDict[analyte][2] = True
							ct.AnalyteDict[analyte][1] = [x for x in metadatalst]
							#append primary key value with the _analyte name
							ct.AnalyteDict[analyte][1][0] += "%s" % analyte
							for field in ct.ColumnList:							
								ct.AnalyteDict[analyte][1].append(line_parced[ct.ColumnIndexDict[field]])
				
				
				if valid_txtfile == True:

					message = 'Analyte data succesfully mined from text file: %s' % metadatalst[2]
					self.EventLogger(message)
					#time.sleep(0.300)
						
					#Verify that each analyte was found, if not 
					#fill each value with "Not Found"
					for analyte in ct.AnalyteLst:
						if ct.AnalyteDict[analyte][2] == False:
							ct.AnalyteDict[analyte][1] = [x for x in metadatalst]
							#append primary key value with the analyte name
							ct.AnalyteDict[analyte][1][0] += "%s" % analyte
							ct.AnalyteDict[analyte][1].append(analyte)
							temp = ['Not Found'] * 9
							ct.AnalyteDict[analyte][1].extend(temp)
							
					#Query to check for data overwrite
					keyword = None
					table = self.D2D_Table
					columns = ["Instrument_SN_date_time_Analyte_Name"]
					condition = "Instrument_SN_date_time_Analyte_Name LIKE '%s%s'" % (metadatalst[0], '%')
					sort = None
					primary_key_check = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)
					
					#if there is no existing data that conflicts with the minded data then upload
					if primary_key_check == []:
						
						for analyte in ct.AnalyteLst:
							values = ct.AnalyteDict[analyte][1]
							self.D2Ddb.Insert_Query_No_Conditions(table, self.D2Ddb_columns, values)
							
						message = 'Analyte data succesfully uploaded to database.'
						self.EventLogger(message)
					#if there is existing data that conflicts with the minded data then prompt overwrite warning
					else:
						display_datetime = self.display_datetime(metadatalst[1])
						#yes = True and no = False
						question = '''There is already data within the database
									matching the dates found in this text file:
									
									File Name: %s
									Time Stamp: %s
									
									Do you wish to replace the existing database records 
									with the new information found within this text file?''' % (metadatalst[2], display_datetime)
						caption = "OVERWRITE WARNING - %s" % metadatalst[2]
						dlg = wx.MessageDialog(self, question, caption, wx.YES_NO | wx.ICON_QUESTION)
						overwrite_data = dlg.ShowModal() == wx.ID_YES
						dlg.Destroy()
						message = "OVERWRITE WARNING - User overwrite data = %s\n\t\tSource File: %s" % (str(overwrite_data), metadatalst[2])
						self.EventLogger(message)
						
						#if the user elects to overwrite then do so 
						if overwrite_data == True:
							
							for analyte in ct.AnalyteLst:
								condition = "Instrument_SN_date_time_Analyte_Name = '%s'" % ct.AnalyteDict[analyte][1][0]
								values = ct.AnalyteDict[analyte][1]
								self.D2Ddb.Update_Query(table, self.D2Ddb_columns, values, condition)
							message = 'Analyte data updated. - %s\n' % metadatalst[2]
							
						#If the user elects not to overwrite then do not update the database 
						elif overwrite_data == False:
							message = 'Omitted - The analyte data within this file has been omitted. - %s\n' % metadatalst[2]
							
						self.EventLogger(message)
							
				elif valid_txtfile == False:
					#The all the headers were not found or the file is imporperly formatted, therefore it will be skipped
					message = "Invalid Formatting - This text file is not properly formatted.\n\t\tSource File: %s\n" % txt_filenames_lst[txtfile_index]
					self.EventLogger(message)

						
		self.EventLogger('Action Complete\n')
		dlg.Destroy()
		
	def OnDisplayData(self, event):
		xyz = True
		message = "Creating Report - Please Wait...\n"
		self.EventLogger(message)
	
		#Get instrument serial number & define a chromatof object
		InstSN = str("%s" % self.instrument_SN_radiobut.GetStringSelection())
		ct = ChromatTOF()
		
		#Define query_columns list that will be used in the set data query
		query_columns = [x for x in self.D2Ddb_columns[1:-1]]
		query_columns.remove('conc_lvl')
		query_columns.remove('analysis_stage')
		query_columns.remove('Instrument_SN')
		query_columns.remove('Day')
		query_columns.remove('Name')
		
		#Get list of every distinct analytical stage found in the database
		
		keyword = 'DISTINCT'
		table = self.D2D_Table
		columns = ['analysis_stage']
		condition = "Instrument_SN = '%s'" % InstSN
		sort = 'analysis_stage ASC'
		anal_stg_lst = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)
		anal_stg_lst = [str("%s" % x) for x in anal_stg_lst]

		if anal_stg_lst == []:
			message = "Insufficent database records to query."
			self.EventLogger(message)
		else:
			
			userhome = os.path.expanduser('~')
			userhome += '\\Desktop\\'
			
			#Iterate through analysis stage
			for stage in anal_stg_lst:
			
				
				#Get list of every distinct concentration level witin the given analytical stage found in the database
				keyword = 'DISTINCT'
				table = self.D2D_Table
				columns = ['conc_lvl']
				condition = "analysis_stage = '%s' AND Instrument_SN = '%s'" % (stage, InstSN)
				sort = 'conc_lvl ASC'
				conc_lvl_lst = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)
				conc_lvl_lst = [str("%s" % x) for x in conc_lvl_lst]
			
				excel_file_namepath = '%s%s_D2D_Stability_Stage_%s.xlsx' % (userhome, InstSN, stage)
				
				xlsx = ExcelFile(excel_file_namepath)
				
				#Iterate thourgh each analyte
				for analyte in ct.AnalyteLst:
				
					analyte_display_name = analyte.replace('"','')
					sheet_name = analyte_display_name[:25]
					xlsx.add_sheet(sheet_name)
				
					#Iterate through concentration level list
					for lvl_index, lvl in enumerate(conc_lvl_lst):
						
						#drop set data headers 
						start_dump_column = self.setdata_startcolumn + (lvl_index * self.setdata_lvl_column_spacer)
						xlsx.add_list_of_lists(self.start_row, start_dump_column, [ct.Set_Data_Headers], 'headers')
						
						#drop set data concentration label & analyte name
						concentration_label = ct.AnalyteDict[analyte][3][lvl]
						data_type = 'string'
						row = self.start_row - 1
						col = start_dump_column + 1
						xlsx.write_cell(row, col, concentration_label, data_type)
						col -= 1
						xlsx.write_cell(row, col, analyte_display_name, data_type)
						
						#Query db for set data
						keyword = None
						table = self.D2D_Table
						condition = "analysis_stage = '%s' AND conc_lvl = '%s' AND Instrument_SN = '%s' AND Name = '%s'" % (stage, lvl, InstSN, analyte)
						sort = 'date_time ASC'
						analyte_record_lst = self.D2Ddb.Select_Query(keyword, table, query_columns, condition, sort)
						
						#drop data
						xlsx.add_list_of_lists(self.start_row + 1, start_dump_column, analyte_record_lst, 'set_data')
						
						#calculate row & column coordinates which will be used in the graphs
						last_row = len(analyte_record_lst) + self.start_row + 1
						voltage_column = start_dump_column + 2
						field_start_column = start_dump_column + 3
						set_data_start_row = self.start_row + 2
						
						field_index = 2
						for index, field in enumerate(ct.Set_Data_Headers[3:]):
							field_column = field_start_column + index
							field_index += 1
							
							#Create graphs
							graph_title = self.ChartTitleGenerator(ct.AnalyteDict[analyte][0], field, analyte, concentration_label)
							graph_row = self.graph_metadata[lvl]['row'] + self.start_row + (self.summarydata_field_row_spacer * index) - 1
							
							xlsx.scatter_plots(sheet_name, start_dump_column, field_column, voltage_column, 
								set_data_start_row, last_row, self.graph_metadata[lvl]['color'], 
								graph_row, self.graph_metadata[lvl]['col'], graph_title, field)
								
							
							#Drop headers
							start_row = self.summarydata_cell_coordinates[lvl]['row'] + self.start_row + (self.summarydata_field_row_spacer * index) - 1
							start_col = self.summarydata_cell_coordinates[lvl]['col'] + self.setdata_startcolumn
							header_1 = [concentration_label, field]
							header_2 = ["", "Ave.", "Std. Dev.", "%RSD"]
							headers = [header_1, header_2]
							xlsx.add_list_of_lists(start_row, start_col, headers, 'headers')
							
							#Get list of every distinct day 
							keyword = 'DISTINCT'
							table = self.D2D_Table
							columns = ['Day']
							condition = "analysis_stage = '%s' AND conc_lvl = '%s' AND Instrument_SN = '%s' AND Name = '%s'" % (stage, lvl, InstSN, analyte)
							sort = 'Day ASC'
							day_lst = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)
							day_lst = [str("%s" % x) for x in day_lst]
							
							#determine individual day summary statistics for a given field and analyte
							for day_index, day in enumerate(day_lst):
							
								#set/reset stats list
								stats_list = ['Day %s' % day]
								
								#define query statement elements
								keyword = None
								table = self.D2D_Table
								columns = [query_columns[field_index]]
								condition = "analysis_stage = '%s' AND conc_lvl = '%s' AND Instrument_SN = '%s' AND Name = '%s' AND Day = '%s'" % (stage, lvl, InstSN, analyte, day)
								sort = None
								
								#query database
								field_day_lst = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)
								stats_list.extend(self.SummaryStats(field_day_lst))
								
								row = start_row + 2 + day_index
								xlsx.add_list_of_lists(row, start_col, [stats_list], 'stats')
							
							
							#determine all days summary statistics for a given field and analyte
							
							#set/reset stats list
							stats_list = ['All Days']
							
							#define query statement elements
							keyword = None
							table = self.D2D_Table
							columns = [query_columns[field_index]]
							condition = "analysis_stage = '%s' AND conc_lvl = '%s' AND Instrument_SN = '%s' AND Name = '%s'" % (stage, lvl, InstSN, analyte)
							sort = None
							
							#query database
							field_all_days_lst = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)
							stats_list.extend(self.SummaryStats(field_all_days_lst))
							
							row += 1
							xlsx.add_list_of_lists(row, start_col, [stats_list], 'stats')
					
					message = "%s Data - Complete" % analyte_display_name					
					self.EventLogger(message)			
				
				message = "Finalizing Stage %s Report Please Wait...\n" % stage					
				self.EventLogger(message)
				xlsx.disconnect()
				xlsx = None			
		
		
		self.EventLogger('Action Complete\n')
	
	def FindReplaceStringInTextFile(self, filename, replacements):
		# Searches text file then finds and replaces give valeus 
		# Requires dictionary where the key is the string to find &
		# the value is the replacement string
		
		# replacements = {"p,p'-DDT_TAF":'p,p-DDT_TAF', "p,p'-DDT":'p,p-DDT'}
		
		tempfile = os.path.join(os.getcwd(), 'temp.txt')

		with open(filename) as infile, open(tempfile, 'w') as outfile:
			for line in infile:
				for OriginalAnalyteName, NewAnalyteName in replacements.iteritems():
					line = line.replace(OriginalAnalyteName, NewAnalyteName)
				outfile.write(line)

		return tempfile
	
	def ChartTitleGenerator(self, DataProcessingType, Field, Analyte, Concentration):
		
		if DataProcessingType == 't':
			proc = "TAF"
		elif DataProcessingType == 'p':
			proc = "Peak Find"
			
		return "%s - %s %s (%s)" % (Field, Analyte, Concentration, proc)
	
	
	def SummaryStats(self, lst):
		stats_list = []
		
		#convert from unicode into a string
		lst = [str("%s" % x) for x in lst]
		
		#remove "Not Found's" and convert srings to float
		float_lst = self.remove_NotFound(lst)
		
		#if all values were "Not Found's" and list is now empty then fill with "No Data"
		if float_lst == []:
			stats_list = ["No Data"] * 3
		
		#Otherwise calculate mean population std and %RSD
		else:
			stats_list.append(s.mean(float_lst))
			stats_list.append(s.pstdev(float_lst))
			temp = (stats_list[1]/stats_list[0]) * 100
			stats_list.append(temp)
		
		return stats_list
	
	def EventLogger(self, message):
		current_time = str(time.strftime("%H:%M:%S"))
		current_date = str(time.strftime("%m/%d/%Y"))
		status_message = "%s %s - %s\n" % (current_date, current_time, message) 
		self.status_logger.AppendText(status_message)

	def Determine_Day(self, date_time, instrument_SN, conc_lvl, analysis_stage, file_name):
		keyword = None
		table = self.D2D_Table
		columns = ['MIN(date_time)']
		condition = "Instrument_SN = '%s' AND conc_lvl = '%s' AND analysis_stage = '%s'" % (instrument_SN, conc_lvl, analysis_stage)
		sort = None
		min_datetime_lst = self.D2Ddb.Select_Query(keyword, table, columns, condition, sort)

		d = "%s" % min_datetime_lst[0]
		
		if d == 'None':
			# print 'file_name: ', file_name
			# print 'conc_lvl: ', conc_lvl
			# print 'analysis_stage: ', analysis_stage 
			# print 'date_time: ', date_time
			# print 
			return "01"
		else:
			d0 = self.DateTimeObject(d)
			d1 = self.DateTimeObject(date_time)
			delta = d1 -d0
			value =  str(int(round(delta.days) + 1)) 
			
			# print 'file_name: ', file_name
			# print 'conc_lvl: ', conc_lvl
			# print 'analysis_stage: ', analysis_stage 
			# print 'date_time: ', date_time
			# print 'd0: ', d0
			# print 'd0: ', d1
			# print 'delta: ', delta
			# print 'value: ', value
			# print
			
			if len(value) != 2:
				return "0" + value
			else:
				return value
	
	def DateTimeObject(self, date_time):
		return datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
	
	def display_datetime(self, database_datetime):
		return datetime.datetime.strptime(database_datetime, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')
		
	def remove_NotFound(self, analyte_data_list):
		#Removes all list elements = "Not Found" and returns list converted to floats
		
		str_lst = [val for val in analyte_data_list if val != "Not Found"]
		return [float(i) for i in str_lst]
	
		
class ChromatTOF():
	def __init__(self):
		
		self.ColumnIndexDict = {}
						
		self.ColumnList = ["Name", "Area", "Similarity", "R.T. (s)", "Height", "FWHH (s)", "Tailing Factor", "Peak S/N", "Quant S/N", "Group"]
		
		self.Set_Data_Headers = ["Date Time", "Source File", "Det. Bias", "Area", "Similarity", "R.T. (s)", "Height", "FWHH (s)", "Tailing Factor", "Peak S/N", "Quant S/N"]

		self.AnalyteLst = ["Perfluoronaphthalene", "OFN", 
							"Bis(pentafluorophenyl)phenyl phosphine", "DFTPP"]
							
		#Data structure of AnalyteDict key = ChromatTOF naming of a given analyte
			#value = [ p = peak found analyte or t = TAF analyte, [] = values to append which will be insert queried, boolean = was analyte found]
		self.AnalyteDict = {"Perfluoronaphthalene": ['p', [], False, {"1": "5 pg", "2": "10 pg", "3": "50 pg", "4": "100 pg"}],
							"OFN": ['t', [], False, {"1": "5 pg", "2": "10 pg", "3": "50 pg", "4": "100 pg"}],
							"Bis(pentafluorophenyl)phenyl phosphine": ['p', [], False, {"1": "5 pg", "2": "10 pg", "3": "50 pg", "4": "100 pg"}],
							"DFTPP": ['t', [], False, {"1": "5 pg", "2": "10 pg", "3": "50 pg", "4": "100 pg"}],}
			
def BackUpProject(source, destination):	
	call(["robocopy", source, destination, "/mir"])
		
print "\n\n\n" + "Start" + "-" * 18 
		
app = wx.App(False)
frame = D2D_Frame(None, title="Day to Day Stability 2.0")
panel = D2D_Panel(frame)
frame.Show(True)
app.MainLoop()

print "END" + "-" * 20 + "\n\n\n"

# BackUpProject("C:\\D2D_Stability", "C:\\D2D_Stability_Backup")


