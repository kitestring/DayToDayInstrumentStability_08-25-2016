  /* 
Delete records from files inadvertately uploaded to the wrong instrument S/N
 */
  
SELECT 'Count before removing inadvertat file uploads.';

SELECT COUNT(*) FROM Analyte_Data;

DELETE FROM Analyte_Data
WHERE 
	file_name = 'D2D Stab. 1D Day-01 L-1 (5 pg on Col) PV2_Result.txt' OR
	file_name = 'D2D Stab. 1D Day-01 L-2 (10 pg on Col) PV2_Result.txt' OR
	file_name = 'D2D Stab. 1D Day-01 L-3 (50 pg on Col) PV2_Result.txt' OR
	file_name = 'D2D Stab. 1D Day-01 L-4 (100 pg on Col) PV2_Result.txt';
	
	
SELECT 'Count after removing inadvertat file uploads.';
SELECT COUNT(*) FROM Analyte_Data;


/*   
Some records do not have values as similalrity scores, which is causeing
a "ValueError: could not convert string to float:" down stream
easiest fix is to pull them out as there are only 3 records with this issue.
 */

  
SELECT file_name, Name, Similarity FROM Analyte_Data
WHERE 
	Instrument_SN = 'VP2' AND
	analysis_stage = '2' AND
	Similarity = '' AND
	Name != 'D2D Stab. GCxGC Day-01 L-3 (50 pg on Col) PV2_Result.txt'
ORDER BY 1 ASC;


SELECT 'Count before removing rows with Similarity = ""';

SELECT COUNT(*) FROM Analyte_Data;
 
DELETE FROM Analyte_Data
WHERE 
	Instrument_SN = 'VP2' AND
	analysis_stage = '2' AND
	Similarity = '';
	
SELECT 'Count after removing rows with Similarity = ""';
SELECT COUNT(*) FROM Analyte_Data;


/*   
Remove all records that were generated with the faulty filament
 */

SELECT 'Record Count Prior to Deletion';

SELECT analysis_stage, day, COUNT(day) FROM Analyte_Data
WHERE 
	Instrument_SN = 'VP2'
	AND  
		((analysis_stage = '1' AND
		date_time < '2017-12-15 14:04:17')
		OR
		(analysis_stage = '2' AND
		date_time < '2017-12-14 14:07:13'))
GROUP BY analysis_stage, day;

DELETE FROM Analyte_Data
WHERE 
	Instrument_SN = 'VP2'
	AND  
		((analysis_stage = '1' AND
		date_time < '2017-12-15 14:04:17')
		OR
		(analysis_stage = '2' AND
		date_time < '2017-12-14 14:07:13'));
		
SELECT 'Record Count After Deletion';
		
SELECT analysis_stage, day, COUNT(day) FROM Analyte_Data
WHERE 
	Instrument_SN = 'VP2'
	AND  
		((analysis_stage = '1' AND
		date_time < '2017-12-15 14:04:17')
		OR
		(analysis_stage = '2' AND
		date_time < '2017-12-14 14:07:13'))
GROUP BY analysis_stage, day;