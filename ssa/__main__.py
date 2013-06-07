# Python dependencies
import argparse
import csv
import math
import os
import sys
import time

# external source dependencies
import requests

# local source dependencies
import es_proxy
import importfile_util



#
# TODO:
# - change key names to something more understandable and more appropriate
#   to the document store paradigm
# - allow user to create multiple types within an index
# - allow user to use a type name different from the index name
# - reorganize argparser so it only accepts certain arguments with the arguments
#   they're MEANT to work with.  it just ignores irrelevant args right now.
#



#
# Add the contents of a tab-delimited file (TDF) to an ElasticSearch database.
#
def import_data(filename, \
    es_server, \
    index_name=None, \
    type_name=None, \
    delete_preexisting_type=False, \
    field_translations=None, \
    mapping=None, \
    username=None, \
    password=None):
    data_lines = importfile_util.retrieve_file_lines(filename)

    if len(data_lines) < 2:
        print "there is no data to import"
        return

    if type_name is None:
        # bugfix
        #filename_no_path = filename.split('\\')[-1]
        # above code assumes windows file locations
        filename_no_path = os.path.basename(filename)
        type_name = filename_no_path.split('.')[0].lower()
        print "setting document type to \"" + type_name + "\""

    if index_name is None:
        index_name = type_name
        print "setting index name to \"" + index_name + "\""

    es = es_proxy.get_es(es_server, username, password)
    is_index_ready = es_proxy.ensure_index(index_name, es)

    if delete_preexisting_type:
        print "clearing existing documents from index"
        es_proxy.clear_documents(index_name, type_name, es)

    if mapping is not None:
        print "applying mapping from " + mapping + " to ElasticSearch"
        mapping_def = importfile_util.retrieve_file(mapping)
        es_proxy.ensure_mapping(index_name, type_name, mapping_def, es)

    if is_index_ready:
        current_count = 0
        current_status = 0
        start_time = time.time()
        total_count = len(data_lines)

        # translate if applicable and then retrieve the field names
        if field_translations is not None:
            reader = translate_fields(data_lines, field_translations)
        else:
            reader = csv.DictReader(data_lines, delimiter="\t")

        print "importing " + str(total_count) + " records from " + filename
        for doc in reader:
            es_proxy.index_doc(doc, index_name, type_name, es)

            # indicate current status
            current_count += 1
            current_status = math.floor(current_count * 100 / total_count)
            sys.stdout.write("\rCurrent Status: %d%%" %current_status)
            sys.stdout.flush()

        # indicate completion
        sys.stdout.write("\rCurrent Status: 100%\n\n")
        sys.stdout.flush()
        end_time = time.time() - start_time
        print "completed bulk import of " + \
            str(total_count) + " documents in " + \
            str(end_time) + " seconds"

    else:
        print "index was not ready for import"

    return



#
# Returns list of field names based on the instructions in a tab-delimited field
# translations file.
#
def translate_fields(data_lines, field_translations_path):
    reader = csv.DictReader(data_lines, delimiter="\t")
    fieldtranslation_lines = importfile_util.retrieve_file_lines(field_translations_path)

    if len(fieldtranslation_lines) < 2:
        return reader

    fieldname_keys = fieldtranslation_lines[0].split("\t")
    fieldname_values = fieldtranslation_lines[1].split("\t")

    return data_filter(reader, fieldname_keys, fieldname_values)



def data_filter(it, keys, fieldvalues):
    for d in it:
        yield dict((fieldvalues[keys.index(k)], d[k]) for k in keys)



#
# Set up the argparser in its own method, for clarity.
#
def set_up_argparser():
    parser = argparse.ArgumentParser(\
        description='Processes tab-delimited files and imports data to the specified ES server')
    parser.add_argument('-s', '--es_server', \
        nargs=1, \
        required=True, \
        help="The ES URI")
    parser.add_argument('-user', '--username', \
        nargs=1, \
        default=[None], \
        help="Username for ES")
    parser.add_argument('-pass', '--password', \
        nargs=1, \
        default=[None], \
        help="Password for ES")
    parser.add_argument('-i', '--index_name', \
        nargs=1, \
        required=True, \
        help="The index for the new data.")
    parser.add_argument('-rm', '--delete_preexisting_type', \
        action="store_true", \
        default=False, \
        help="Remove any docs of specified type prior to import")
    parser.add_argument('-f', '--filename', \
        nargs=1, \
        help="Tab-delimited file to import into ES")
    parser.add_argument('-map', '--map_file_path', \
        nargs=1, \
        default=[None], \
        help="Mapping file for specified type")
    parser.add_argument('-fn', '--field_name_translations_path', \
        nargs=1, \
        default=[None], \
        help="Translation file between mapping and tab-delimited columns.")
    parser.add_argument('-t', '--type_name', \
        nargs=1, \
        default=[None], \
        help="The type for the documents to import.")

    return parser



#
# The main method.
#
def main(argv):
    argparser = set_up_argparser()
    args = argparser.parse_args()
    es_server = args.es_server[0]

    if args.index_name is not None:
        index_name = args.index_name[0]
    else:
        index_name = None

    if args.filename is not None:
        if os.path.isfile(args.filename[0]):
            if args.type_name is not None:
                type_name = args.type_name[0]
            else:
                type_name = None

            import_data(args.filename[0], \
                es_server, \
                index_name=index_name, \
                type_name=type_name, \
                mapping=args.map_file_path[0], \
                field_translations=args.field_name_translations_path[0], \
                delete_preexisting_type=args.delete_preexisting_type, \
                username = args.username[0], \
                password = args.password[0])

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
