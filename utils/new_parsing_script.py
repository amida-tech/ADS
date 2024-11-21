import pandas as pd


Name_of_Code_Set = "" # Enter name of condition(Arrythmias, GI Cancer etc.)
file_name = ""  #Enter file name stored in input folder

input_directory = f"codeset/input/{file_name}.xlsx"
output_directory = f"codeset/output/{Name_of_Code_Set}.txt"

default = pd.read_excel(input_directory, sheet_name="Code Set Details")

df = default.drop(default[default['In CDW'] == 'No'].index)

#splitting phrases if they have a semicolon
df['Code Set'] = df['Code Set'].str.split().str.join("")

df['CFR Criteria'] = df['CFR Criteria'].str.split('; ')
df = df.explode('CFR Criteria')

top_dicts = df['CFR Criteria'].unique()

nested_dict = {}

for unique_val in top_dicts:
   nested_dict[unique_val] = {"Tuple Code Set": ()}

#Code works by utilizing dictionary data structure. Keys are the CFR criteria and the values are tuples(Code Set, Code). A different for loop runs for every Code Set(NDC, ICD-10 etc.) and consolidates codes by both CFR criteria as well as code set. Output is a text file.


#creating tuples of Code Set and Code(NDC, CPT, ICD-9, IDC-10)
df['Tuple'] = list(zip(df['Code Set'], df["Code"]))

#Making dictionary: Key = CFR Criteria and Value = tuple of Code Set + Code combo
main = (df.groupby('CFR Criteria')['Tuple'].apply(list).to_dict())


#creating tuples of Code Set and Code(Keyword)
df['Tuple_part_2'] = list(zip(df['Code Set'], df["Code Description"]))

keyword_dict = (df.groupby('CFR Criteria')['Tuple_part_2'].apply(list).to_dict())



with open(output_directory, "w") as f:

    f.write(f"{Name_of_Code_Set} \n\n")

    #Compiles all LOINC Codes
    for k,v in main.items():
        loinc_appender = []
        for code_type, code in v:
            if code_type == "LOINC":
                loinc_appender.append(str(code))
        loincs = f"{k} LOINC codeset:\n '{','.join(loinc_appender)}'\n"

        if len(loinc_appender) > 0:
            f.write(f"{loincs} \n")
    f.write("\n\n\n") 



    #Compiles all ICD-10 Codes
    for k,v in main.items():      
        icd_10_appender = []
        for code_type, code in v:
            if code_type == "ICD-10":
                icd_10_appender.append(str(code))
        icd_10 = f"{k} ICD-10 codeset:\n '{','.join(icd_10_appender)}'\n"

        if len(icd_10_appender) > 0:
            f.write(f"{icd_10} \n")
    f.write("\n\n\n") 


    #Compiles all CPT Codes   
    for k,v in main.items():
        cpt_appender = []
        for code_type, code in v:
            if code_type == "CPT":
                cpt_appender.append(str(code))
        cpt = f"{k} CPT codeset:\n '{','.join(cpt_appender)}'\n"


        
        if len(cpt_appender) > 0:
            f.write(f"{cpt} \n")
    f.write("\n\n\n") 

    #Compiles all ICD -9 Codes
    for k,v in main.items():
        icd_9_appender = []
        for code_type, code in v:
            if code_type == "ICD-9":
                icd_9_appender.append(str(code))
        icd_9 = f"{k} ICD-9 codeset:\n '{','.join(icd_9_appender)}'\n"



        if len(icd_9_appender) > 0:
            f.write(f"{icd_9} \n")
    f.write("\n\n\n") 

    #Compiles NDC Codes
    for k,v in main.items():
        ndc_appender = []
        for code_type, code in v:
            if code_type == "NDC":
              ndc_appender.append(f"{str(code)}%")
        ndc = f"{k} NDC codeset:\n '{','.join(ndc_appender)}'\n"


        if len(ndc_appender) > 0:
            f.write(f"{ndc} \n")
    f.write("\n\n\n")

    #Compiles all SNOMED-CT Codes   
    for k,v in main.items():
        cpt_appender = []
        for code_type, code in v:
            if code_type == "SNOMED-CT":
                cpt_appender.append(str(code))
        cpt = f"{k} SNOMED-CT codeset:\n '{','.join(cpt_appender)}'\n"


        
        if len(cpt_appender) > 0:
            f.write(f"{cpt} \n")
    f.write("\n\n\n") 

    #Compiles Keyword Codes
    for k,v in keyword_dict.items():
        keyword_appender = []
        for code_type, code in v:
            if code_type == "Keyword":
                keyword_appender.append(f"%{str(code)}%")
        keyword = f"{k} Keyword codeset:\n '{','.join(keyword_appender)}'\n"


        if len(keyword_appender) > 0:
            f.write(f"{keyword} \n")
    f.write("\n\n\n")



f.close()
        
      








 
 

            

   