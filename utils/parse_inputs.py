# text file name to update

icd10_input = 'test-icd10'
icd9_input = 'test-icd9'
cpt_input = 'test-cpt'
ndc_input = ''
keyword_input = 'test-kw'
output_filename = 'test_output'

# parse input files
def read_inputs(filename, code):
    """
    Summary: Parses and concatenate input values depending on codeset type (ICD, CPT, NDC, etc.)
    Args: filename(str): filename located in input folder
          code(str): type of code set (icd, cpt, keyword)
    Returns: string: code set values
    """

    with open(f'codeset/input/{filename}.txt', "r") as file:

        # parses and split text files into specific lists for inputs to sql query
        if code == 'icd10-group' or code == 'icd10' or code == 'icd9':
            if code == 'icd10-group':
                codeset = "".join(f"{line.rstrip()[:3]}," for line in file)
                codeset = list(set(codeset.split(",")))
                codeset = ','.join(filter(None, codeset))

            if code == 'icd10' or code == 'icd9':
                codeset = "".join(f"{line.rstrip()}," for line in file)
                codeset = codeset.rstrip(',')
            
        if code == 'cpt':
            codeset = "".join(f"{line.rstrip()}," for line in file)
            codeset = codeset.rstrip(',')

        if code == 'ndc':
             codeset = "".join(f"{line.rstrip()[:10]}%," for line in file)

        if code == 'keyword':
            codeset = "".join(f"%{line.rstrip()[:10]}%," for line in file)
            codeset = codeset.rstrip(',')

    return f'{code} codeset: {codeset} ============================'


if __name__ == '__main__':

    code_list = [(icd10_input,'icd10-group'), (icd10_input,'icd10'), (icd9_input,'icd9'), (cpt_input,'cpt'), (ndc_input, 'ndc'), (keyword_input, 'keyword')]
    
    # loops through each type of codeset
    with open(f'codeset/output/{output_filename}.txt','a') as txtfile:
        for filename, code in code_list:
                if filename is None or filename == '':
                    pass
                else:
                    txtfile.write(f'{read_inputs(filename, code)}\n')
