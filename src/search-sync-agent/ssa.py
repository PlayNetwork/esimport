import sys
import os
import time

import argparse
import csv

import pyes


#
# TODO:
# - change key names to something more understandable
#



def add_tdf_to_elasticsearch(filename, es_server, index_name=None, delete_preexisting_index=False):
    remove_bom_from_utf8(filename)
    
    if index_name is None:
        filename_no_path = filename.split('\\')[-1]
        index_name = filename_no_path.split('.')[0].lower()
    
    conn = pyes.ES(es_server)
    index_is_ready = verify_es_index(index_name, conn, delete_preexisting_index)

    sys.stdout.write("Adding TDF data to ElasticSearch...")
    sys.stdout.flush()

    start_time = time.time()
    if index_is_ready:
        doc_count = 0
        with open(filename, 'rb') as tdf_file:
            reader = csv.DictReader(tdf_file, delimiter='\t')

            for row in reader:
                # for now, index name matches the type
                conn.index(row, index_name, index_name)
                
                doc_count += 1
                if (doc_count % 1000) == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()

        conn.indices.refresh(index_name)

    elapsed_time = time.time() - start_time
    print "done!  Completed in " + str(elapsed_time) + " seconds."



# UTF-8 files generated on Windows machines generally start with a byte-order
# mark.  We need to remove the BOM so the DictReader doesn't use it as part
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
# Adds the contents of all files in a directory with the specified extension(s)
# to an ES database.
# Assumption: The original files are TDF format.
#
def add_tdfs_in_dir_to_elasticsearch(path, es_server, extensions=('.txt', '.tdf'), \
                             delete_preexisting_indices=False):
    add_all_start_time = time.time()
    
    directory = os.listdir(path)

    if not path.endswith("\\"):
        path += "\\"

    files_added_count = 0
    
    for f in directory:
        if f.endswith(extensions):
            print f
            add_tdf_to_elasticsearch(path + f, es_server, \
                    delete_preexisting_index=delete_preexisting_indices)
            files_converted_count += 1
            print ""
    
    add_all_elapsed_time = time.time() - add_all_start_time
    print "Adding data from " +str(files_added_count) + \
          " files to ElasticSearch took " + str(add_all_elapsed_time) + \
          " seconds."

    return files_converted_count



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
# Dev test method; not meant for inclusion in non-dev branches.
#
def test_es(es_server):
    conn = pyes.ES(es_server)

    q = pyes.TermQuery("Is_A_Timezone_Folder", False)   # they're all false, this is the easiest way to get all records.
    results = conn.search(query=q)
    
    num_results = len(results)
    max_to_print = 20
    for r in results[:max_to_print]:
        print r

    if num_results > max_to_print:
        print "Printed the first " + str(max_to_print) + " results."

    print str(num_results) + " results found!"
    print conn.get_indices()



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

    parser = argparse.ArgumentParser(description='Process TDF files and add \
                                     them to an ElasticSearch database.')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-f', '--files', nargs='+', \
                       help="TDF files that need to be added to ElasticSearch.")
    group.add_argument('-d', '--dirs', nargs='+', \
                       help="Directories containing TDF files that need to be \
                             added to ElasticSearch.  If -ext is not \
                             specified, only files ending in " + \
                             default_extensions_string + " will be processed.")
    group.add_argument('-test', '--run_test', \
                        action="store_true", default=False, \
                        help="Test query to verify presence of data.")
    group.add_argument('-i', '--get_indices', action="store_true", \
                       default=False, help="Get summary of indices.")

    parser.add_argument('-ext', '--extensions', nargs='+', \
                        default=default_input_extensions, \
                        help="File extensions to process when processing an \
                              entire directory.  If not specified, defaults \
                              to " + default_extensions_string)
    parser.add_argument('-s', '--es_server', nargs=1, required=True, \
                        help="The ElasticSearch database's server and port.")
    parser.add_argument('-del', '--delete_preexisting_index', \
                        action="store_true", default=False, \
                        help="Before adding docs to an index, delete the index \
                              if it already exists.")

    return parser.parse_args()



#
# The main method.
#
def main(argv):
    args = set_up_argparser()

    operation_start_time = time.time()

    # Construct user-friendly summary of operations run
    friendly_list_of_ops = []

    if args.files is not None:
        for f in args.files:
            add_tdf_to_elasticsearch(f, args.es_server, \
                    delete_preexisting_index=args.delete_preexisting_index)
        
        friendly_list_of_ops.append("adding " + str(len(args.files)) + \
                                    " file(s) to the ElasticSearch database")

    if args.dirs is not None:
        files_converted = 0
        for d in args.dirs:
            files_converted += add_tdfs_in_dir_to_elasticsearch(d, \
                    args.es_server, extensions=tuple(args.extensions), \
                    delete_preexisting_indices=args.delete_preexisting_index)

        friendly_list_of_ops.append("adding " + str(files_converted) + \
                " files in " + str(len(args.paths)) + " directories to the \
                 ElasticSearch database")

    if args.run_test == True:
        test_es(args.es_server)
        friendly_list_of_ops.append("running a test query on the ES database")

    if args.get_indices == True:
        print pyes.ES(args.es_server).get_indices()

    operation_elapsed_time = time.time() - operation_start_time

    if len(friendly_list_of_ops) > 0:
        operation_description = ""

        # construct description of what just happened
        for op in friendly_list_of_ops:
            # add separator between last op description and this one
            if friendly_list_of_ops[0] is op:    # first item
                pass
            elif friendly_list_of_ops[-1] is op: # last item
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
