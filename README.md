# Day-to Day InstrumentStability

### Date Written: 08/25/2016

### Industry: Time of Flight Mass Spectrometer Developer & Manufacturer

### Department: Validation (Late Stage R&D)

### GUI Example:
![GUI.png](/Examples/GUI.png)

### Experiment Description:

The primary object of this experiment was to determine the stability and reproducibility of the instrument over a 25 day period of time.  This was quantified by measuring 4 different chemical mixtures which contained 36 chemicals of interest at 4 different concentration levels.  Each concentration level was measured ten times each day for a total of 40 measurements each day.  This was done across three different instruments.  For each chemical there were 9 metrics to assess the performance.  After each measurement, the instrument would export a single tab delimited text file.  

### Data Accumulation:

If you’ve been doing the math that’s 40 text files per day X 25 days X 3 instruments = 3,000 text files.  Taking it a step further, each text file contained between 70 & 120 chemicals that were detected in the chemical mixture, 36 being relevant to the study.  Each chemical had 9 metrics that we were interested in.  Therefore each text file contained 324 values of interest.  Thus, this experiment generated 3,000 X 324 = 972,000 values critical to our instigation.

### Sample Output:
![SampleOutput_Area-Perfluoronaphthalene](/Examples/SampleOutput_Area-Perfluoronaphthalene.png)
 THis is an example of the integrated area plotted for all four concentration levels of the chemical Perfluoronaphthalene after 10 days of the investigation.  A secondary y-axis is included overlaying the instrument detector voltage was set to for a particular measurement.
 
### Application Description:

This application has two basic functionalities: 
  1. Mine the appropriate chromatographic data from the text files and load it into a SQL data base.  
  1. Display the data by creating a new excel file with a worksheet for each chemical.  

Then querying the SQL database and dumping the corresponding chemical data into its respective worksheet.  Each worksheet contains 4 data tables, one for each concentration level.  Finally, each of the nine metrics has 4 graphs, one for each concentration level.  Each plot has a secondary y-axis that overlays the detector voltage the instrument was set to for that particular measurement.

Having the ability to continually append the SQL database each day of the investigation, and subsequently, generate new excel files with the latest data, allowed me monitor the data during the course of the experiment.  This turned out to be a critical advantage as I was able to very quickly and easily identify and address any anomalous behavior that popped during the course of the investigation.
