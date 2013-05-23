import sys
import os
import time

import argparse
import csv
import json

import pyes


#
# TODO:
# - change key names to something more understandable
# - for readability, perhaps break out argparser and extensions string
#   setup into their own method?
#



# UTF-8 files generated on windows machines generally start with a byte-order
# mark.  We need to remove the BOM so the dictreader doesn't use it as part
# of a column header.  If it doesn't have the BOM, this won't hurt anything.
def remove_bom_from_utf8(filename):
    with open(filename, 'rb') as f:
        original_contents = f.read()

    sys.stdout.write("Checking TDF file format for BOM... ")
    sys.stdout.flush()

    start_time = time.time()

    decoded_contents = original_contents.decode('utf-8-sig').encode('utf-8')

    elapsed_time = time.time() - start_time
    print "done!  Completed in " + str(elapsed_time) + " seconds."
    

    # if the conversion changed anything, write the new version to the file
    if original_contents != decoded_contents:
        sys.stdout.write("BOM located and removed.  Writing new file... ")
        sys.stdout.flush()
        
        start_time = time.time()

        with open(filename, 'w') as f:
            f.write(decoded_contents)

        elapsed_time = time.time() - start_time
        print "done!  Completed in " + str(elapsed_time) + " seconds."
    else:
        print "No BOM found, so no file changes are required."



#
# Converts the specified file to JSON format.
#
# Assumptions:
#   - Specified file is a tab-delimited file (TDF)
#   - It's OK to overwrite any existing files in that directory
#     that have the same name except a .json extension.
#
def tdf_to_json (filename):
    method_start_time = time.time()

    remove_bom_from_utf8(filename)

    with open(filename, 'rb') as tdf:
        sys.stdout.write("reading in TDF... ")  # print next info on same line
        sys.stdout.flush()

        start_time = time.time()

        reader = csv.dictreader(tdf, delimiter='\t')
        data = json.dumps([r for r in reader], indent=4, separators=(',', ': '))

        elapsed_time = time.time() - start_time
        print "done!  Completed in " + str(elapsed_time) + " seconds."
    
    json_filename = filename.split('.')[0] + '.json'

    with open(json_filename, 'w') as json_file:
        sys.stdout.write("Writing JSON file... ")
        sys.stdout.flush()

        start_time = time.time()

        json_file.write(data)

        elapsed_time = time.time() - start_time
        print "done!  Completed in " + str(elapsed_time) + " seconds."

    method_elapsed_time = time.time() - method_start_time
    print "Done converting TDF to JSON!"
    print "The conversion for " + filename + " took " + \
          str(method_elapsed_time) + " seconds."
    print "JSON data can be found at " + json_filename + "."



#
# Converts all files in a directory with the specified extension to
# JSON format.  It is assumed that the original files are TDF format.
#
def convert_all_tdf_in_dir(path, extension=('.txt', '.tdf')):
    convert_all_start_time = time.time()
    
    directory = os.listdir(path)

    if not path.endswith("\\"):
        path += "\\"

    files_converted_count = 0
    
    for f in directory:
        if f.endswith(extension):
            print f
            tdf_to_json(path + f)
            files_converted_count += 1
            print ""
    
    convert_all_elapsed_time = time.time() - convert_all_start_time
    print "Converting " +str(files_converted_count) + " files took " + \
          str(convert_all_elapsed_time) + " seconds."



#
# Verifies that a specified index exists and creates it if not.
# Optional behavior: delete existing index and recreate it.
#
def verify_es_index(index_name, conn, delete_existing_index=False):
    try:
        if delete_existing_index:
            conn.indices.delete_index_if_exists(index_name)

        conn.indices.create_index_if_missing(index_name)
        return True
    except:
        print "Unexpected error: ", sys.exc_info()

    return False



#
# Processes the specified JSON file and pushes the JSON data into
# the specified ElasticSearch database.
#
# Assumption: the JSON file's name, minus the extension, is also the
# name of the index that should contain the data.
#
def send_json_to_elasticsearch(filename, es_ip):
    start_time = time.time()
    sys.stdout.write("Reading in JSON file... ")  # print next info on same line
    sys.stdout.flush()

    with open(filename, 'rb') as json_file:
        data = json.load(json_file)

    elapsed_time = time.time() - start_time
    print "done!  Completed in " + str(elapsed_time) + " seconds."
    
    filename_no_path = filename.split("\\")[-1]
    index_name = filename_no_path.split(".")[0].lower()
    #print index_name
    
    conn = pyes.ES(es_ip)
    delete_index_first = True
    index_exists = verify_es_index(index_name, conn, \
            delete_existing_index=delete_index_first)

    start_time = time.time()
    sys.stdout.write("Adding JSON data to index " + index_name + "... ")  # print next info on same line
    sys.stdout.flush()

    if index_exists:
        try:
            for row in data:
                # for now, index name matches the type
                conn.index(row, index_name, index_name)
            conn.indices.refresh(index_name)

        except:
            print "unexpected error: ", sys.exc_info()[0]
    else:
        print "\nCould not add data to ElasticSearch; index '" + index_name + \
              "' does not exist!"
    
    elapsed_time = time.time() - start_time
    print "done!  Completed in " + str(elapsed_time) + " seconds."
    


#
# Runs a simple query to verify existence of data in an index.
# Dev testbed method; not meant for inclusion in non-dev branches.
#
def test_es(es_ip):
    conn = pyes.ES(es_ip)

    q = pyes.TermQuery("Is_A_Timezone_Folder", False)   # they're all false, this is the easiest way to get all records.
    results = conn.search(query=q)
    
    num_results = len(results)
    max_to_print = 20
    for r in results[:max_to_print]:
        print r

    if num_results > max_to_print:
        print "Printed the first " + str(max_to_print) + " results."

    print str(num_results) + " results found!"



#
# Set up the argparser in its own method, for clarity.
#
def set_up_argparser():
    default_input_extensions = ['.txt']
    default_extensions_string = ""

    for extension in default_input_extensions:
        default_extensions_string += extension
        if extension is not default_input_extensions[-1]:
            if len(default_input_extensions) > 1:
                default_extensions_string += "; "

    parser = argparse.ArgumentParser(description='Process TDF and JSON files, \
                                     and send them to an ElasticSearch database.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--files', nargs='+', \
                       help="TDF files that need to be converted to \
                             JSON-format files.")
    group.add_argument('-p', '--paths', nargs='+', \
                       help="Directories containing TDF files that need to be \
                             converted to JSON-format files.  If -ext is not \
                             specified, only files ending in " + \
                             default_extensions_string + " will be processed.")
    group.add_argument('-j2es', '--json_to_es', nargs='+', \
                       help="Add the specified JSON-format file(s) to \
                       an ElasticSearch database.")
    group.add_argument('-test', '--run_test', \
                        action="store_true", default=False, \
                        help="Test query to verify presence of data.")

    parser.add_argument('-ext', '--input_extensions', nargs='+', \
                        default=default_input_extensions, \
                        help="Extensions of files that need to be processed \
                        when processing an entire directory.  If not \
                        specified, defaults to " + default_extensions_string)
    parser.add_argument('-ei', '--es_ip', nargs=1, \
                        help="IP and port of the ElasticSearch database.")

    return parser.parse_args()



#
# The main method.  argparser setup lives here for the time being.
#
def main(argv):
    args = set_up_argparser()

    operation_start_time = time.time()

    # Construct user-friendly summary of operations run
    friendly_list_of_ops = []

    if args.files is not None:
        for f in args.files:
            tdf_to_json(f)
        friendly_list_of_ops.append("converting " + str(len(args.files)) + \
                                    " file(s)")

    if args.paths is not None:
        for path in args.paths:
            convert_all_tdf_in_dir(path, tuple(args.input_extensions))
            print ""

        friendly_list_of_ops.append("converting files in " + \
                                    str(len(args.paths)) + " directories")

    if args.es_ip is not None:
        if args.json_to_es is not None:
            for f in args.json_to_es:
                send_json_to_elasticsearch(f, args.es_ip)
            friendly_list_of_ops.append("sending JSON file to ES database")

        if args.run_test == True:
            test_es(args.es_ip)
            friendly_list_of_ops.append("running test query on ES database")

    operation_elapsed_time = time.time() - operation_start_time

    if len(friendly_list_of_ops) > 0:
        operation_description = ""

        # construct description of what just happened
        for op in friendly_list_of_ops:
            # add separator between last op description and this one
            if friendly_list_of_ops[0] is op:    # first item
                pass
            elif friendly_list_of_ops[-1] is op: #last item
                operation_description += " and "
            else:
                operation_description += "; "
            
            operation_description += op.strip()

        # Would love to use .capitalize() here, but it makes everything
        # that is NOT the first char lowercase!
        operation_description = operation_description[:1].upper() + operation_description[1:]
        print operation_description + " took " + \
              str(operation_elapsed_time) + " seconds."



if __name__ == "__main__":
    main(sys.argv[1:])
