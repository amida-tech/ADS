# Medical Code presence in Arrhythmias Dataset

## GEMs Backward Mapping
This script validates the presence of medical codes in the CDW by ingesting an original file where medical codes were identified. The script should adjust code formats for accurate matching and populate the original file with a "Yes" or "No" in the "In CDW" column to indicate whether each code is present in the CDW.



## Understanding Results
A new spreadsheet will be created where the presence of each code in the CDW will be represented as Yes or No. 

## Inputs
- any dataset with columns containing at LEAST 'Code Set', 'Code', 'Code Description' and 'In CDW'. Ideally the 'In CDW' column will be blank. If not, the script will overwrite anything in that column. 

## Outputs
- Excel file containing the following columns:'Code Set', 'Code', 'Code Description' and 'In CDW' + any other columns. 
