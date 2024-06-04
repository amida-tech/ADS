import pandas as pd
import warnings

warnings.filterwarnings('ignore')

#This code will cross check whether codes are present in the CDW and label the 'In CDW' column with either 'Yes' or 'No'. Script assumes that there are sheets labeled as icd10-cpt-loinc and ndc-snomed-icd9.
#Script also assumes that in sheet name icd10-cpt-loinc, there are column names labeled as CodeSet, Code and Description. Sheet name ndc-snomed-icd9 should have columns CodeSet, NDC and LocalDrugNameWithDose.


#medical codes file
file_path = r"codeset/input/med_codes.xlsx"# This is the CDW. Make sure an updated version is inside the input folder or change the file path to where it is stored. 

sheet_name_icd10_loinc_cpt = "icd10-cpt-loinc"
sheet_name_ndc_snomed_icd9 = "ndc-snomed-icd9"
med_codes_icd10_loinc_cpt = pd.read_excel(file_path, sheet_name= sheet_name_icd10_loinc_cpt)
med_codes_ndc_snomed_icd9 = pd.read_excel(file_path, sheet_name= sheet_name_ndc_snomed_icd9)

#Codes to Check- Enter any medical codes file here. Example file is arrhythmias medical codes.
file_path_1 = r"codeset/input/arrhythmias_codes.xlsx"  # File with codes to check. Make sure an updated version is in the input folder. There should be a column labeled as 'In CDW' which should be blank.
sheet_name = "Code Set Details"
confirmed_codes = pd.read_excel(file_path_1, sheet_name=sheet_name)
confirmed_codes['Code'] = confirmed_codes['Code'].astype(str)



#NDC values format adjustment. Uses boolean mask to check if values have the CodeSet of "NDC". Then performs format adjustment using regex.
is_ndc = med_codes_ndc_snomed_icd9['CodeSet'] == 'NDC'
med_codes_ndc_snomed_icd9.loc[is_ndc, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ndc, 'NDC'].str[:-3]


#ICD-10 values format adjustment. Uses boolean mask to check if values have the CodeSet of "ICD-10". Then performs format adjustment using regex.
is_ICD_10 = med_codes_icd10_loinc_cpt['CodeSet'] == 'ICD-10'
med_codes_icd10_loinc_cpt.loc[is_ICD_10, 'Code'] = med_codes_icd10_loinc_cpt.loc[is_ICD_10, 'Code'].str.replace(r'^([A-Za-z0-9]+)$', r'\1.', regex=True)

#ICD-9 values format adjustment. Uses boolean mask to check if values have the CodeSet of "NDC". Then performs format adjustment using regex.
is_ICD_9 = med_codes_ndc_snomed_icd9['CodeSet'] == 'ICD-9'
med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'].str.replace(r'^(\d+)$', r'\1.0', regex=True)

#ICD-9 values format adjustment in codes to check file(ex. changes 150 to 150.0)
for index, row in confirmed_codes.iterrows():
    if row['Code Set'] == 'ICD-9' and '.' not in row['Code']:
        confirmed_codes.at[index, 'Code'] = f"{row['Code']}.0"



#Remove trailing zeros from decimal values-small but important test case
#med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'].str.replace(r'(\.\d*[1-9])0+$', r'\1', regex=True)



#First if statement in for loop covers keyword checks. Else statement covers NDC, ICD-10, CPT etc., and labels 'Yes' or 'No' in the 'in_cdw' column.
        
for index_cs, code_set_val in confirmed_codes["Code Set"].items():
    if code_set_val == 'Keyword':
        temp_desc = confirmed_codes.at[index_cs, "Code Description"]
        in_cdw = med_codes_ndc_snomed_icd9['LocalDrugNameWithDose'].str.contains(temp_desc, case =False).any()
        confirmed_codes.at[index_cs, "In CDW"] = 'Yes' if in_cdw else 'No'

    else:
        temp = confirmed_codes.at[index_cs, "Code"]
        in_cdw = med_codes_icd10_loinc_cpt['Code'].eq(temp).any() or med_codes_ndc_snomed_icd9['NDC'].eq(temp).any()
        confirmed_codes.at[index_cs, "In CDW"] = 'Yes' if in_cdw else 'No'



#Update output file path to desired output file path. A new file 'confirmed_codes' will be generated with values representing if codes are found in CDW. 

output_file_path = r'codeset/output/confirmed_codes.xlsx'
confirmed_codes.to_excel(output_file_path, index=False)

