# text file name to update

icd_input = 'icd_brain'
cpt_input = ''
ndc_input = 'gi_ndc'
keyword_input = ''
output_filename = 'test_output'

# parse input files
def read_inputs(filename, code):
    """
    Summary: Parses and concatenate input values depending on codeset type (ICD, CPT, NDC, etc.)
    Args: filename(str): filename located in input folder
          code(str): type of code set (icd, cpt, keyword)
    Returns: string: code set values
    """

    with open(f'./utils/codeset/input/{filename}.txt', "r") as file:

        # parses and split text files into specific lists for inputs to sql query
        if code == 'icd' or code == 'icd-current':
            if code == 'icd':
                codeset = "".join(f"{line.rstrip()[:3]}," for line in file)
                codeset = list(set(codeset.split(",")))
                codeset = ','.join(filter(None, codeset))

            if code == 'icd-current':
                codeset = "".join(f"{line.rstrip()}," for line in file)
                codeset = codeset.rstrip(',')
            
        if code == 'cpt' or code == 'snomed':
            codeset = "".join(f"{line.rstrip()}," for line in file)
            codeset = codeset.rstrip(',')

        if code == 'ndc':
            codeset = "".join(f"{line.rstrip()[:13]}%," for line in file)

        if code == 'keyword':
            codeset = "".join(f"CPTName LIKE '%{line.rstrip()}%' OR " for line in file)

    return f'{code} codeset: {codeset} ============================'


if __name__ == '__main__':

    code_list = [(icd_input,'icd'), (icd_input,'icd-current'), (cpt_input,'cpt'), (ndc_input, 'ndc'), (keyword_input, 'keyword')]
    
    # loops through each type of codeset
    with open(f'./utils/codeset/output/{output_filename}.txt','a') as txtfile:
        for filename, code in code_list:
                if filename is None or filename == '':
                    pass
                else:
                    txtfile.write(f'{read_inputs(filename, code)}\n')
