import pandas as pd
import warnings

warnings.filterwarnings('ignore')

#This code will cross check whether Arrythmias codes are present in the CDW and label the 'In CDW' column with either 'Yes' or 'No'. 

#medical codes file
file_path = "C:\\Users\\standard\\Desktop\\ExcelCodeData\\med_codes.xlsx" # This is the CDW. Make sure an updated version is inside the input folder
sheet_name_icd10_loinc_cpt = "icd10-cpt-loinc"
sheet_name_ndc_snomed_icd9 = "ndc-snomed-icd9"
med_codes_icd10_loinc_cpt = pd.read_excel(file_path, sheet_name= sheet_name_icd10_loinc_cpt)
med_codes_ndc_snomed_icd9 = pd.read_excel(file_path, sheet_name= sheet_name_ndc_snomed_icd9)

#Arrythmias codes
file_path_1 = "C:\\Users\\standard\\Desktop\\ExcelCodeData\\arryth_codes.xlsx" #Arrythmias Codes. Make sure an updated version is in the input folder. There should be a column labeled as 'In CDW' which should be blank. 
sheet_name = "Code Set Details"
arry_codes = pd.read_excel(file_path_1, sheet_name=sheet_name)

#NDC values
is_ndc = med_codes_ndc_snomed_icd9['CodeSet'] == 'NDC'
med_codes_ndc_snomed_icd9.loc[is_ndc, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ndc, 'NDC'].str[:10]

#ICD-10 values
is_ICD_10 = med_codes_icd10_loinc_cpt['CodeSet'] == 'ICD-10'
med_codes_ndc_snomed_icd9['NDC'] = med_codes_ndc_snomed_icd9['NDC'].str.replace(r'(\d+)\..*', r'\1')

#ICD-9 values
is_icd_9 = med_codes_ndc_snomed_icd9['CodeSet'] == 'ICD-9'
med_codes_ndc_snomed_icd9['NDC'] = med_codes_ndc_snomed_icd9['NDC'].str.replace(r'([A-Za-z0-9]+)\..*', r'\1')

#Keywords
for (index_cs, code_set_val), (index_code, code_val) in zip(enumerate(arry_codes["Code Set"]), enumerate(arry_codes["Code"])):
    if code_set_val == 'Keyword':
        temp_desc = arry_codes.at[index_cs, "Code Description"]
        if med_codes_ndc_snomed_icd9['LocalDrugNameWithDose'].str.contains(temp_desc, case =False).any():
            arry_codes.at[index_cs, "In CDW"] = str('Yes')
        else:
            arry_codes.at[index_cs, "In CDW"] = str('No')

    else:
        temp = arry_codes.at[index_code, "Code"]
        if med_codes_icd10_loinc_cpt['Code'].str.startswith(temp).any() or med_codes_ndc_snomed_icd9['NDC'].str.startswith(temp).any():
            arry_codes.at[index_code, "In CDW"] = str('Yes')
        else:
            arry_codes.at[index_code, "In CDW"] = str('No')


output_file_path = 'C:\\Users\\standard\\Desktop\\ExcelCodeData\\arry_codes.xlsx'
arry_codes.to_excel(output_file_path, index=False)

#print(arry_codes[['Code Set', 'Code', 'Code Description', 'In CDW']].iloc[501:514])
#print(arry_codes[(arry_codes['In CDW'] == 'Yes') & (arry_codes['Code Set'] == 'NDC')][['Code Set', 'Code', 'In CDW']])
