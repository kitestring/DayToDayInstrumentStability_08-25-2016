/* 
Remove the outliers in the VP1 GCxGC Area - DFTPP 5 pg (TAF) data set
 */
 

SELECT 'Count before VP1 GCxGC Area - DFTPP 5 pg (TAF) outliers';
SELECT COUNT(*) FROM Analyte_Data;
SELECT file_name, Instrument_SN, Area FROM Analyte_Data
WHERE
	(Name = 'DFTPP' AND
	Instrument_SN = 'VP1' AND
	analysis_stage = '2' AND
	conc_lvl = '1') 
	AND
	(CAST(AREA as Float) < 600000 OR
	Area = 'Not Found');
SELECT '';

DELETE FROM Analyte_Data
WHERE
	(Name = 'DFTPP' AND
	Instrument_SN = 'VP1' AND
	analysis_stage = '2' AND
	conc_lvl = '1') 
	AND
	(CAST(AREA as Float) < 600000 OR
	Area = 'Not Found');
	
	
SELECT 'Count after VP1 GCxGC Area - DFTPP 5 pg (TAF) outliers';
SELECT COUNT(*) FROM Analyte_Data;


/* 
Remove the outliers in the VP1 GCxGC 
Area - Bis(pentafluorophenyl)phenyl phosphine 5 pg (Peak Find)
data set
 */
 
  
SELECT 'Count before VP1 GCxGC Area - Bis(pentafluorophenyl)phenyl phosphine 5 pg (Peak Find)';
SELECT COUNT(*) FROM Analyte_Data;
SELECT file_name, Instrument_SN, Area FROM Analyte_Data
WHERE
	Name = 'Bis(pentafluorophenyl)phenyl phosphine' AND
	Instrument_SN = 'VP1' AND
	analysis_stage = '2' AND
	conc_lvl = '1' AND
	Similarity = 'Not Found';
SELECT '';

DELETE FROM Analyte_Data
WHERE
	Name = 'Bis(pentafluorophenyl)phenyl phosphine' AND
	Instrument_SN = 'VP1' AND
	analysis_stage = '2' AND
	conc_lvl = '1' AND
	Similarity = 'Not Found';
SELECT '';
		
SELECT 'Count after VP1 GCxGC Area - Bis(pentafluorophenyl)phenyl phosphine 5 pg (Peak Find)';
SELECT COUNT(*) FROM Analyte_Data;



/* 
Remove the outliers in the VP2 GCxGC 
Area - OFN 5 pg (TAF) and
Similarity - Bis(pentafluorophenyl)phenyl phosphine 5 pg (Peak Find)
Area - DFTPP 5 pg (TAF)
data sets
 */
 
SELECT file_name, Instrument_SN, Area, Name, Area, analysis_stage FROM Analyte_Data
WHERE
	(Name = 'OFN' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '1' AND
	conc_lvl = '1' AND
	CAST(AREA as Float) < 10500000)
	OR
	(Name = 'Bis(pentafluorophenyl)phenyl phosphine' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '1' AND
	conc_lvl = '1' AND
	Similarity = 'Not Found')
	OR
	(Name = 'DFTPP' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '1' AND
	conc_lvl = '1' AND
	Similarity = 'Not Found')
	OR
	(Name = 'OFN' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '2' AND
	conc_lvl = '1' AND
	((CAST(AREA as Float) < 12000000) OR
	(CAST(AREA as Float) > 16000000)))
	OR
	(Name = 'DFTPP' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '2' AND
	conc_lvl = '1' AND
	CAST(AREA as Float) > 2700000)
ORDER BY analysis_stage, Name ASC;
SELECT '';

DELETE FROM Analyte_Data
WHERE
	(Name = 'OFN' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '1' AND
	conc_lvl = '1' AND
	CAST(AREA as Float) < 10500000)
	OR
	(Name = 'Bis(pentafluorophenyl)phenyl phosphine' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '1' AND
	conc_lvl = '1' AND
	Similarity = 'Not Found')
	OR
	(Name = 'DFTPP' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '1' AND
	conc_lvl = '1' AND
	Similarity = 'Not Found')
	OR
	(Name = 'OFN' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '2' AND
	conc_lvl = '1' AND
	((CAST(AREA as Float) < 12000000) OR
	(CAST(AREA as Float) > 16000000)))
	OR
	(Name = 'DFTPP' AND
	Instrument_SN = 'VP2' AND
	analysis_stage = '2' AND
	conc_lvl = '1' AND
	CAST(AREA as Float) > 2700000);