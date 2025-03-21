import requests # pylint: disable=import-error
import pandas as pd # pylint: disable=import-error

## CHANGE INPUTS HERE ##
API_KEY = 'YOUR API KEY HERE'

# Output Excel Sheet Name
CONDITION = 'CONDITION NAME'

# Input Excel Sheet with Keywords Name
CSV_FILE_INPUT_NAME = 'CONDITION KEYWORDS FILE NAME'

## END OF REQUESTED INPUTS ##

# Keyword Column Name
COLUMN_NAME = 'Keyword'

# Read the Excel file
df = pd.read_csv('input/' + CSV_FILE_INPUT_NAME + '.csv')
df = df[df["Data Concept"] == "Medication"]

# Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
# 'CFR Criteria' by a semicolon if there are multiple entries for the same
# keyword
df = df.groupby('Keyword').agg({
    'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
    'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
    'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
    'Code Set': 'first'  # Retain 'Code Set' as it doesn't need concatenation
}).reset_index()

# Extract the column as a Pandas Series
column_series = df[COLUMN_NAME]

# Remove "\" or "/" values from the column_series
column_series = column_series.str.replace(r'[\/\\]', ' ', regex=True)

# Replace double or triple spaces with single spaces
column_series = column_series.str.replace(r'\s{2,}', ' ')
column_series = column_series.str.replace(r'\s{3,}', ' ')

# Convert the Pandas Series to a list and exclude the column name as the
# first element
column_list = [keyword.replace(' ', '+') for keyword in column_series.tolist()]

string_list = column_list
df["Keyword"] = string_list

# Now column_list contains the column data with the column name as the
# first element
print(string_list)


def query_openFDA(keyword): # pylint: disable=invalid-name, missing-function-docstring
    # Query for generic_name
    # Note: Some generics DONT have a brand_name variable
    url_generic = f"https://api.fda.gov/drug/ndc.json?API_KEY={API_KEY}&search=generic_name:{keyword}&limit=1000" # pylint: disable=line-too-long
    response = requests.get(url_generic)

    if response.status_code == 200:
        data = response.json() # pylint: disable=line-too-long
        meta = data.get("meta")

        if meta:
            total_results = meta.get("results", {}).get("total", 0)
            limit = meta.get(
                "results", {}).get(
                "limit", 1)  # check this for the limit

            if total_results > limit:
                print(
                    f'Warning: Total results for {keyword} exceed the specified limit.')
            else:
                print(f'Query for generic_name {keyword} successful. \n')

        else:
            print(
                f'Warning: Metadata not found in the response for {keyword}.')

        if data.get("results"):
            return data["results"]

    else:
        print(
            f'generic_name: Failed to fetch data from openFDA API for {keyword}.')

    # If generic_name search fails, try brand_name
    url_brand = f"https://api.fda.gov/drug/ndc.json?API_KEY={API_KEY}&search=brand_name:{keyword}&limit=1000" # pylint: disable=line-too-long
    response = requests.get(url_brand)

    if response.status_code == 200:
        data = response.json() # pylint: disable=line-too-long
        meta = data.get("meta")

        if meta:
            total_results = meta.get("results", {}).get("total", 0)
            limit = meta.get("results", {}).get("limit", 1)

            if total_results > limit:
                print(
                    f'Warning: Total results for {keyword} exceed the specified limit.')
            else:
                print(f'Query for brand_name {keyword} successful. \n')

        else:
            print(
                f'Warning: Metadata not found in the response for {keyword}.')

        if data.get("results"):
            return data["results"]
    else:
        print(
            f'brand_name: Failed to fetch data from openFDA API for {keyword}.')


def process_data(results, keyword, original_row):
    records = []
    for result in results:
        generic_name = result.get("generic_name")
        brand_name = result.get("brand_name")
        packaging = result.get("packaging", [])
        strength = result.get("active_ingredients", [{}])[0].get("strength")
        marketing_category = result.get("marketing_category")
        for package in packaging:
            package_ndc = package.get("package_ndc")
            description = package.get("description")
            drug_name_with_dose = (
                f'{generic_name} ' if generic_name else f'{brand_name} ') + (
                f'{strength} ' if strength else '')
            records.append([
                package_ndc, drug_name_with_dose,
                original_row['VASRD Code'],
                original_row['Data Concept'],
                original_row['CFR Criteria'],
                original_row['Code Set'],
                keyword,
                marketing_category
            ])
    return records


def main(df_input):
    records = []
    for _, row in df_input.iterrows():
        keyword = row['Keyword']
        results = query_openFDA(keyword)
        if results:
            records += process_data(results, keyword, row)
        else:
            print(f"No data found for keyword: {keyword}")

    df_api_results = pd.DataFrame(records, columns=[
        "Code", 
        "Code Description", 
        "VASRD Code", 
        "Data Concept", 
        "CFR Criteria", 
        "Code Set", 
        "Keyword", 
        "MarketingCategory"
    ])
    return df_api_results


if __name__ == "__main__":
    # Example list of keywords
    df_processed = main(df)

    # Format the NDC codes

    ndc_list = df_processed['Code']

    formatted_ndc_list = []
    # Formats the first 5 values XXXXX-AAAA-BB (X values)
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
            print(
                f'IndexError for NDC code:{ndc}, check NDC code in final output')

    formatted_ndc_list_2 = []

    # Formats the second 4 values XXXXX-AAAA-BB (A values)
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
            print(
                f'IndexError for NDC code:{ndc}, check NDC code in final output')

    formatted_ndc_list_3 = []

    # Formats the last 2 values XXXXX-AAAA-BB (B values)
    # Note: B values are not needed in the final output, but are required to
    # clean for the remove_suffix function to work as intended
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
            print(
                f'IndexError for NDC code:{ndc}, check NDC code in final output')

    df_processed['Code'] = formatted_ndc_list_3

    # This removes the additional 51655-0856-XX from the end of the NDC code.
    def remove_suffix(df, column_name):
        df[column_name] = df[column_name].str.replace(
            r'-\d{2}$', '', regex=True)
        return df

    df_processed = remove_suffix(df_processed, 'Code')

    # Remove duplicate NDC codes
    # Group by 'Keyword' and concatenate 'VASRD Code', 'Data Concept', and
    # 'CFR Criteria' by a semicolon if there are multiple entries for the same
    # keyword
    NDC_full_grouped = df_processed.groupby('Code').agg({
        'VASRD Code': lambda x: '; '.join(x.astype(str).unique()),
        'Data Concept': lambda x: '; '.join(x.astype(str).unique()),
        'CFR Criteria': lambda x: '; '.join(x.astype(str).unique()),
        'Code Set': 'first',  # Retain 'Code Set' as it doesn't need concatenation
        'Code Description': 'first',
        'Keyword': lambda x: '; '.join(x.astype(str).unique()),
        'MarketingCategory': lambda x: '; '.join(x.astype(str).unique())
    }).reset_index()

    # Save file
    OUTPATH = 'output/'
    FILE_NAME = f"{CONDITION}_NDC_codes.xlsx"
    NDC_full_grouped.to_excel(OUTPATH + FILE_NAME)

    # Print a message indicating where the file is saved
    print(f"Excel file '{FILE_NAME}' saved in the output folder.")
