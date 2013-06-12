# Python dependencies
import argparse
import os
import sys

# local source dependencies
import esimport



DELIMITER_DEFAULT = ","



#
# Set up the argparser in its own method, for clarity.
#
def set_up_argparser():
	parser = argparse.ArgumentParser(\
		description="Processes tab-delimited files and imports data to the specified ES server")

	parser.add_argument("-d", "--delimiter", \
		nargs=1, \
		default=[DELIMITER_DEFAULT], \
		help="delimiter between columns in the import file (defaults to ',')")
	parser.add_argument("-i", "--index_name", \
		nargs=1, \
		required=True, \
		help="the index for the new data.")
	parser.add_argument('-f', '--filename', \
		nargs=1, \
		required=True, \
		help="tab-delimited file to import into ES")
	parser.add_argument("-m", "--map_file_path", \
		nargs=1, \
		default=[None], \
		help="file containing JSON mapping for specified type")
	parser.add_argument("-n", "--field_translations_path", \
		nargs=1, \
		default=[None], \
		help="translation file between mapping and tab-delimited columns")
	parser.add_argument("-pass", "--password", \
		nargs=1, \
		default=[None], \
		help="password for Basic Authentication")
	parser.add_argument("-rm", "--delete_type", \
		action="store_true", \
		default=False, \
		help="remove any docs of specified type prior to import")
	parser.add_argument('-s', '--server', \
		nargs=1, \
		required=True, \
		help="ElasticSearch URI")
	parser.add_argument("-t", "--type_name", \
		nargs=1, \
		required=True, \
		help="type name for the documents to import")
	parser.add_argument("-user", "--username", \
		nargs=1, \
		default=[None], \
		help="username for Basic Authentication")
	parser.add_argument("-nv", "--skip_verify", \
		action="store_false", \
		help="if ES requires SSL, this setting allows you to bypass certificate validation")

	return parser



#
# The main method.
#
def main(argv):
	argparser = set_up_argparser()
	args = argparser.parse_args()

	if os.path.isfile(args.filename[0]):
		esimport.import_data(args.filename[0], \
			delimiter=args.delimiter[0].decode("string-escape"), \
			server=args.server[0], \
			index_name=args.index_name[0], \
			type_name=args.type_name[0], \
			mapping=args.map_file_path[0], \
			field_translations=args.field_translations_path[0], \
			delete_type=args.delete_type, \
			username = args.username[0], \
			password = args.password[0],
			verify = args.skip_verify)

		sys.exit(0)
	else:
		print "Error: filename argument supplied is not a file"
		argparser.print_help()
		sys.exit(1)



#
# Run as module
#
if __name__ == "__main__":
	main(sys.argv[1:])
