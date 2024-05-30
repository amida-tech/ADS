import pandas as pd
import warnings

warnings.filterwarnings('ignore')

#This code will cross check whether codes are present in the CDW and label the 'In CDW' column with either 'Yes' or 'No'. Script assumes that there are sheets labeled as icd10-cpt-loinc and ndc-snomed-icd9.
#Script also assumes that in sheet name icd10-cpt-loinc, there are column names labeled as CodeSet, Code and Description. Sheet name ndc-snomed-icd9 should have columns CodeSet, NDC and LocalDrugNameWithDose.


#medical codes file
file_path = r"C:\Users\standard\Desktop\ExcelCodeData\med_codes.xlsx"  # This is the CDW. Make sure an updated version is inside the input folder. 

sheet_name_icd10_loinc_cpt = "icd10-cpt-loinc"
sheet_name_ndc_snomed_icd9 = "ndc-snomed-icd9"
med_codes_icd10_loinc_cpt = pd.read_excel(file_path, sheet_name= sheet_name_icd10_loinc_cpt)
med_codes_ndc_snomed_icd9 = pd.read_excel(file_path, sheet_name= sheet_name_ndc_snomed_icd9)

#Codes to Check
file_path_1 = file_path_1 = r"C:\Users\standard\Desktop\ExcelCodeData\arryth_codes.xlsx"  # File with codes to check. Make sure an updated version is in the input folder. There should be a column labeled as 'In CDW' which should be blank.
#File with codes to check. Make sure an updated version is in the input folder. There should be a column labeled as 'In CDW' which should be blank. 
sheet_name = "Code Set Details"
arry_codes = pd.read_excel(file_path_1, sheet_name=sheet_name)

#NDC values format adjustment. Uses boolean mask to check if values have the CodeSet of "NDC". Then performs format adjustment using regex.
is_ndc = med_codes_ndc_snomed_icd9['CodeSet'] == 'NDC'
med_codes_ndc_snomed_icd9.loc[is_ndc, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ndc, 'NDC'].str[:10]

#ICD-10 values format adjustment. Uses boolean mask to check if values have the CodeSet of "ICD-10". Then performs format adjustment using regex.
is_ICD_10 = med_codes_icd10_loinc_cpt['CodeSet'] == 'ICD-10'
med_codes_icd10_loinc_cpt.loc[is_ICD_10, 'Code'] = med_codes_icd10_loinc_cpt.loc[is_ICD_10, 'Code'].str.replace(r'^([A-Za-z0-9]+)$', r'\1.', regex=True)

#ICD-9 values format adjustment. Uses boolean mask to check if values have the CodeSet of "NDC". Then performs format adjustment using regex.
is_ICD_9 = med_codes_ndc_snomed_icd9['CodeSet'] == 'ICD-9'
med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'].str.replace(r'^(\d+)$', r'\1.0', regex=True)
# Remove trailing zeros from decimal values-small but important test case
med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'] = med_codes_ndc_snomed_icd9.loc[is_ICD_9, 'NDC'].str.replace(r'(\.\d*[1-9])0+$', r'\1', regex=True)



#First if statement in for loop covers keyword checks. Else statement covers NDC, ICD-10, CPT etc., and labels 'Yes' or 'No' in the 'in_cdw' column.
for (index_cs, code_set_val), (index_code, code_val) in zip(arry_codes["Code Set"].items(), arry_codes["Code"].items()):
    if code_set_val == 'Keyword':
        temp_desc = arry_codes.at[index_cs, "Code Description"]
        in_cdw = med_codes_ndc_snomed_icd9['LocalDrugNameWithDose'].str.contains(temp_desc, case =False).any()
        arry_codes.at[index_cs, "In CDW"] = 'Yes' if in_cdw else 'No'

    else:
        temp = arry_codes.at[index_code, "Code"]
        in_cdw = med_codes_icd10_loinc_cpt['Code'].eq(temp).any() or med_codes_ndc_snomed_icd9['NDC'].eq(temp).any()
        arry_codes.at[index_code, "In CDW"] = 'Yes' if in_cdw else 'No'


output_file_path = r'C:\Users\standard\Desktop\ExcelCodeData\arry_codes.xlsx'
arry_codes.to_excel(output_file_path, index=False)

