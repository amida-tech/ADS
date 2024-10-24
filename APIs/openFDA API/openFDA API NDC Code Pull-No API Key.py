#!/usr/bin/env python
# coding: utf-8

import requests 
import pandas as pd
import os

apikey = 'YOUR API KEY HERE'

#Output Excel Sheet Name
Excel_Sheet_Name = "EXCEL SHEET NAME HERE"

#Input Excel Sheet with Keywords Name
excel_file_keywords = 'GI Cancer Med Keywords.xlsx'

# Keyword Column Name
column_name = 'Keywords'

## End of Requested Inputs ##

# Read the Excel file
excel_file_path = excel_file_keywords
df = pd.read_excel(excel_file_path)

# Extract the column as a Pandas Series
column_series = df[column_name]

# Remove "\" or "/" values from the column_series
column_series = column_series.str.replace(r'[\/\\]', ' ', regex=True)

# Replace double or triple spaces with single spaces
column_series = column_series.str.replace(r'\s{2,}', ' ')
column_series = column_series.str.replace(r'\s{3,}', ' ')

# Convert the Pandas Series to a list and exclude the column name as the first element
column_list = [keyword.replace(' ', '+') for keyword in column_series.tolist()]

# Uncomment this line if you want to include the column name in the keyword search 
# column_list = [keyword.replace(' ', '+') for keyword in [column_name]] + [keyword.replace(' ', '+') for keyword in column_series.tolist()]

modified_list = ['"' + word + '"' for word in column_list]
string_list = modified_list

# Now column_list contains the column data with the column name as the first element
print(string_list)


def query_openFDA(keyword):
    # Query for generic_name
    # Note: Some generics DONT have a brand_name variable
    url_generic = f"https://api.fda.gov/drug/ndc.json?api_key={apikey}&search=generic_name:{keyword}&limit=1000"
    response = requests.get(url_generic)
    
    if response.status_code == 200:
        data = response.json()
        meta = data.get("meta")
        
        if meta:
            total_results = meta.get("results", {}).get("total", 0)
            limit = meta.get("results", {}).get("limit", 1) #check this for the limit
            
            if total_results > limit:
                print(f'Warning: Total results for {keyword} exceed the specified limit.')
            else:
                print(f'Query for generic_name {keyword} successful. \n')
                
        else:
            print(f'Warning: Metadata not found in the response for {keyword}.')
            
        if data.get("results"):
            return data["results"]
    
    else:
        print(f'generic_name: Failed to fetch data from openFDA API for {keyword}.')
    
    # If generic_name search fails, try brand_name
    url_brand = f"https://api.fda.gov/drug/ndc.json?api_key={apikey}&search=brand_name:{keyword}&limit=1000"
    response = requests.get(url_brand)
    
    if response.status_code == 200:
        data = response.json()
        meta = data.get("meta")
        
        if meta:
            total_results = meta.get("results", {}).get("total", 0)
            limit = meta.get("results", {}).get("limit", 1)
            
            if total_results > limit:
                print(f'Warning: Total results for {keyword} exceed the specified limit.')
            else:
                print(f'Query for brand_name {keyword} successful. \n')
                
        else:
            print(f'Warning: Metadata not found in the response for {keyword}.')
            
        if data.get("results"):
            return data["results"]
    else:
        print(f'brand_name: Failed to fetch data from openFDA API for {keyword}.')


def process_data(results):
    records = []
    for result in results:
        generic_name = result.get("generic_name")
        brand_name = result.get("brand_name")
        packaging = result.get("packaging", [])
        strength = result.get("active_ingredients", [{}])[0].get("strength")
        for package in packaging:
            package_ndc = package.get("package_ndc")
            description = package.get("description")
            drug_name_with_dose = (f'{generic_name} ' if generic_name else f'{brand_name} ') + (f'{strength} ' if strength else '')
            records.append([package_ndc, drug_name_with_dose])
    return records

def main(keywords):
    records = []
    for keyword in keywords:
        results = query_openFDA(keyword)
        if results:
            records += process_data(results)
        else:
            print(f"No data found for keyword: {keyword} \n")
    df = pd.DataFrame(records, columns=["NDC", "DrugNameWithDose"])
    
        # Drop duplicate rows based on the 'NDC' column
    df.drop_duplicates(subset=['NDC'], inplace=True)
    
    return df

if __name__ == "__main__":
    # Example list of keywords
    df = main(string_list)

    ndc_list = df['NDC']

    formatted_ndc_list = []

    for ndc in ndc_list:
        parts = ndc.split('-')
        try:
            product_code = parts[1]
            if len(product_code) == 3:
                parts[1] = product_code.zfill(4)  # Add leading zero
                formatted_ndc_list.append('-'.join(parts))
            else:
                formatted_ndc_list.append(ndc)
        except IndexError:
            formatted_ndc_list.append(ndc)
            print(f'IndexError for NDC code:{ndc}, check NDC code in final output')
            
    formatted_ndc_list_2 = []
    
    for ndc in formatted_ndc_list:
        parts = ndc.split('-')
        try:
            labeler_code = parts[0]
            if len(labeler_code) == 4:
                parts[0] = labeler_code.zfill(5)  # Add leading zero
                formatted_ndc_list_2.append('-'.join(parts))
            else:
                formatted_ndc_list_2.append(ndc)
        except IndexError:
            formatted_ndc_list_2.append(ndc)
            print(f'IndexError for NDC code:{ndc}, check NDC code in final output')

    formatted_ndc_list_3 = []

    for ndc in formatted_ndc_list_2:
        parts = ndc.split('-')
        try:
            package_code = parts[2]
            if len(package_code) == 1:
                parts[2] = package_code.zfill(2)  # Add leading zero
                formatted_ndc_list_3.append('-'.join(parts))
            else:
                formatted_ndc_list_3.append(ndc)
        except IndexError:
            formatted_ndc_list_3.append(ndc)
            print(f'IndexError for NDC code:{ndc}, check NDC code in final output')
    
    df['NDC'] = formatted_ndc_list_3

    def remove_suffix(df, column_name):
        df[column_name] = df[column_name].str.replace(r'-\d{2}$', '', regex=True)
        return df
    
    df = remove_suffix(df, 'NDC')

    # Remove duplicate NDC codes
    df.drop_duplicates(subset=['NDC'], inplace=True)

    # Find the parent folder "GitHub Saved Progress"
    parent_folder_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    # Define the output folder path
    output_folder_path = os.path.join(parent_folder_path, "output")

    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
        print(f"Folder 'output' created successfully.")

    # Define the excel file name with its path
    excel_file_path = os.path.join(output_folder_path, f'{Excel_Sheet_Name}.xlsx')

    # Write DataFrame to an Excel file
    with pd.ExcelWriter(excel_file_path) as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)

    # Print a message indicating where the file is saved
    print(f"Excel file '{Excel_Sheet_Name}.xlsx' saved in the 'output' folder.")


