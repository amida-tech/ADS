# """
# Defines the entry point for using these tools from the command line.
# Defines all cli arguments and subcommands and calls appropriate functions based on args.
# """
# import argparse
# import logging
# import excel
# import utils
# from dotenv import load_dotenv

# load_dotenv()


# def retrieve_cdw_data(subparsers):
#     """
#     Defines the validate_xsd_to_csv_file_wrapper subcommand. Looks for a matching XSD and CSV file pair.
#     Checks to make sure identifiers are a match between the documents

#     :param subparsers: subparsers object to attach the subcommand to
#     :type subparsers: subparsers
#     """
#     description = "Displays any differences between the XSD and CSV file pair"
#     help_msg = ""
#     parser = subparsers.add_parser(
#         "retrieve_cdw_data",
#         description=description,
#         help=f"{description}: {help_msg}",
#     )
#     parser.add_argument(
#         "-icd",
#         "--icd-input-path",
#         metavar="icd-input-path",
#         nargs="?",
#         default="./input/",
#         help="File path of where to obtain the necessary XSD file (default: %(default)s)",
#     )
#     parser.add_argument(
#         "-cpt",
#         "--cpt-path",
#         metavar="cpt-txt-path",
#         nargs="?",
#         default="./input/",
#         help="File path of where to obtain the necessary CSV file (default: %(default)s)",
#     )
#     parser.add_argument(
#         "-keywords",
#         "--keywords-path",
#         metavar="keywords-txt-path",
#         nargs="?",
#         default="./input/",
#         help="File path of where to obtain the necessary CSV file (default: %(default)s)",
#     )
#     parser.add_argument(
#         "-o",
#         "--output-filename",
#         metavar="output-csv-path",
#         nargs="?",
#         default="./output/",
#         help="File path of where to obtain the necessary CSV file (default: %(default)s)",
#     )

#     parser.set_defaults(func=utils.retrieve_cdw_data)


# def main():
#     """
#     Defines the top level command and args. Takes care of verbosity and actually calling function with args.
#     """
#     # Top level parser
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-v", "--verbose", help="set log level to INFO", action="store_true")
#     parser.add_argument("-vv", "--very-verbose", help="set log level to DEBUG", action="store_true")
#     subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

#     # broken into functions solely for the sake of organization
#     retrieve_cdw_data(subparsers)

#     args = parser.parse_args()

#     logging.basicConfig()
#     # set verbosity level
#     if args.verbose:
#         logging.getLogger().setLevel(logging.INFO)
#     if args.very_verbose:
#         logging.getLogger().setLevel(logging.DEBUG)

#     # func is set for each command parser
#     func = args.func

# if __name__ == "__main__":
#     main()
