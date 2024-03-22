"""
Script to connect to the relevant CDW tables for pulling specific codesets
"""
# import dependencies
import os
import argparse
import sys
from datetime import date
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

# load variables from environment
SERVER_HOSP = os.getenv("SERVER_HOSP")
DRIVER = os.getenv("DRIVER")
DB = os.getenv("DB")

# Please update these input file names

# icd_input = ''
# keyword_input = ''
cpt_input = 'cpt_current'
output_file = "test_cpt"


# parse input files
def read_inputs(filename, code):
    """
    Summary: Parses and concatenate input values depending on codeset type
    Args: filename(str): filename located in input folder
          code(str): type of code set (icd, cpt, keyword)
    Returns: string: code set values
    """
    with open(f'./cdw/input/{filename}.txt', "r") as file:

        if code == 'icd':
            test = "".join(f"{line.rstrip()[:3]}," for line in file)
            test = set(test.split(","))

        if code == 'cpt':
            test = "".join(f"{line.rstrip()}," for line in file)
            test = test.rstrip(',')

        if code == 'keyword':
            test = "".join(f"CPTName LIKE '%{line.rstrip()}%' OR " for line in file)

    return test


codes = f"'{read_inputs(cpt_input, 'cpt')}'"
# print(codes)

# SQL query parameters
def param_query(codes):
    """
    Summary: SQL query statements used to retrieve data from CDW
    Args: codes (str): list of code sets from the input files
    Returns: (str) a sql query statement
    """
    
    fields = [
        "CPT.CPTCode",
        "CPT.CPTName",
        "CPT.CPTDescription"
    ]

    def_table_join = """
    CDWWork.Dim.CPT CPT
    """
    filter_criteria = f"""
    CPT.CPTCode IN (SELECT * FROM string_split({codes}, ','))
    """

    return f"""SELECT DISTINCT {", ".join(fields)} FROM {def_table_join} WHERE {filter_criteria}"""

def retrieve_cdw_data():
    """
    Summary: COnnect to CDWWork database and retrieve applicable data using SQL
    Args: none for now
    Returns: (object) a csv file containing data from CDW
    """
    engine_cdw = sql.create_engine(f"mssql+pyodbc://{SERVER_HOSP}/{DB}?driver={DRIVER}")
    
    # Check if connection is valid, if not throws type of error from sqlalchemy
    try:
        engine_cdw.connect()
        print("success")
    except SQLAlchemyError as err:
        print("error", err.__cause__)

    # read query into a pandas df
    ads_df = pd.read_sql_query(param_query(codes), engine_cdw)
    ads_df.reset_index()

    # save output as csv
    ads_df.to_csv(f"./cdw/output/{output_file}.csv", index = False)

def main():
    #  # load command line argument
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-o", "--output_file_name", type=argparse.FileType('w', encoding='UTF-8'), help='output file')
    # args = parser.parse_args()
    
    # run cdw query
    retrieve_cdw_data()

if __name__ == '__main__':
    main()