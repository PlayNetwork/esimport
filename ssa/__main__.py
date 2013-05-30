import sys
import os
import time

import argparse
import csv

import pyes
import requests


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
def add_tdf_to_elasticsearch(filename, es_server, index_name=None, \
                             delete_preexisting_index=False, field_translations=None, \
                             mapping=None, es_basic_auth=None):
    remove_bom_from_utf8(filename)
    
    if field_translations is not None:
        rename_tdf_fields(filename, field_translations)
    
    if index_name is None:
        filename_no_path = filename.split('\\')[-1]
        index_name = filename_no_path.split('.')[0].lower()
    
    conn = pyes.ES(es_server, basic_auth=es_basic_auth)
    index_is_ready = verify_es_index(index_name, conn, delete_preexisting_index)
    
    if mapping is not None:
        # assume for now that type name should be the same as index name
        mapping_result = apply_mapping(index_name, index_name, es_server, mapping, \
                                       es_basic_auth=es_basic_auth)

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

    sys.stdout.write("Checking " + filename + " for BOM... ")
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
#
#
def rename_tdf_fields(tdf_path, field_translations_path):
    # ensure the byte-order mark won't trip us up
    print field_translations_path
    remove_bom_from_utf8(field_translations_path)

    field_delimiter_char = '\t'
    
    with open(field_translations_path, 'rb') as translations_file:
        translations_reader = csv.DictReader(translations_file, delimiter=field_delimiter_char)
        field_translations_dict = translations_reader.next()
        
    with open(tdf_path, 'rb') as f:
        original_contents = f.read()
            
    # original data file is written by a Windows machine, so it uses
    # CRLF instead of just LF
    crlf = '\r\n'
    tdf_data = original_contents.split(crlf)
    
    # grab the first line, and turn it into an array of field names
    field_names = tdf_data[0].split(field_delimiter_char)
    
    # replace the original field names in the array with the new ones
    field_name_was_changed = False  # let's be sure we're not doing unnecessary work!
    for i in xrange(len(field_names)):
        if field_names[i] in field_translations_dict:
            field_names[i] = field_translations_dict[field_names[i]]
            field_name_was_changed = True
    
    if field_name_was_changed:
        # put it all back together...
        header = field_delimiter_char.join(field_names)
        tdf_data[0] = header
        new_contents = crlf.join(tdf_data)
        
        with open(tdf_path, 'w') as f:
            f.write(new_contents)



#
# Adds the contents of all files in a directory with the specified extension(s)
# to an ES database.
# Assumption: The original files are TDF format.
#
def add_tdfs_in_dir_to_elasticsearch(path, es_server, tdf_extensions=['.txt', '.tdf'], \
                             mapping_extensions=['.map'], delete_preexisting_indices=False, \
                             field_translations_extensions=None, es_basic_auth=None):
    add_all_start_time = time.time()
    
    directory = os.listdir(path)

    if not path.endswith("\\"):
        path += "\\"

    files_added_count = 0
    
    for f in directory:
        if f.endswith(tuple(tdf_extensions)):
            print f
            
            index_name = f.split('.')[0]
            
            field_translation_path = None
            if field_translations_extensions is not None:
                field_translation_path = find_file_with_extension(path, index_name, field_translations_extensions)
            
            mapping_path = None
            if mapping_extensions is not None:
                mapping_path = find_file_with_extension(path, index_name, mapping_extensions)
            
            add_tdf_to_elasticsearch(path + f, es_server, \
                    delete_preexisting_index=delete_preexisting_indices, \
                    es_basic_auth=es_basic_auth, mapping=mapping_path, \
                    field_translations=field_translation_path)
            files_added_count += 1
            print ""
    
    add_all_elapsed_time = time.time() - add_all_start_time
    print "Adding data from " + str(files_added_count) + \
          " files to ElasticSearch took " + str(add_all_elapsed_time) + \
          " seconds."

    return files_added_count



#
# Looks for a file in a given folder that ends with one of the given extensions.
# If no matching file can be found, returns None.
#
def find_file_with_extension(path, filename_base, extensions):
    # look for a file that is the index name and ends with
    # one of the supplied extensions
    for ext in extensions:
        try:
            path_to_check = path + filename_base + ext
            with open(path_to_check):
                valid_path = path_to_check
                return valid_path
        except IOError:
            pass
        
    return None



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
# Apply the mapping in the supplied file to a type under an index.
#
def apply_mapping(index_name, type_name, es_server, map_filename, es_basic_auth=None):
    # ensure the byte-order mark won't trip us up
    remove_bom_from_utf8(map_filename)
    
    with open(map_filename, 'rb') as f:
        mapping_data = f.read()
    
    # put the mapping to the index.  if ES server is '10.129.1.210:9200',
    # index_name is 'songindex', type_name is 'songtype', and
    # map_filename is \\skynyrd\Export\Dev\data\Song.map', this is equivalent to
    #     curl -XPUT 'http://10.129.1.210:9200/songindex/songtype/_mapping' -d @'\\skynyrd\Export\Dev\data\Song.map'
    put_mapping_address = 'http://' + es_server + '/' + index_name + \
                          '/' + type_name + '/_mapping'
    
    requests_basic_auth = None
    if es_basic_auth is not None:
        requests_basic_auth = requests.auth.HTTPBasicAuth(es_basic_auth['username'], \
                                                          es_basic_auth['password'])
    
    request = requests.put(put_mapping_address, data=mapping_data, \
                           auth=requests_basic_auth)
    return request



#
# Dev test method; not meant for inclusion in non-dev branches.
#
def test_es(es_server, es_basic_auth=None):
    conn = pyes.ES(es_server, basic_auth=es_basic_auth)

    q = pyes.query.MatchAllQuery()
    results = conn.search(q)
    
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
    # specify default extensions for TDF files
    default_tdf_extensions = ['.txt']
    default_tdf_extensions_string = ""

    for extension in default_tdf_extensions:
        default_tdf_extensions_string += extension
        if extension is not default_tdf_extensions_string[-1]:
            if len(default_tdf_extensions) > 1:
                default_tdf_extensions_string += "; "

    # specify default extensions for map files
    default_map_extensions = ['.txt']
    default_map_extensions_string = ""

    for extension in default_map_extensions:
        default_map_extensions_string += extension
        if extension is not default_map_extensions_string[-1]:
            if len(default_map_extensions) > 1:
                default_map_extensions_string += "; "

    parser = argparse.ArgumentParser(description='Process TDF files and add \
                                     them to an ElasticSearch database.')

    group = parser.add_mutually_exclusive_group(required=True)

    # mutually exclusive group
    group.add_argument('-f', '--files', nargs='+', \
                       help="TDF files that need to be added to ElasticSearch.")
    group.add_argument('-d', '--dirs', nargs='+', \
                       help="Directories containing TDF files that need to be \
                             added to ElasticSearch.  If -ext is not \
                             specified, only files ending in " + \
                             default_tdf_extensions_string + " will be processed.")
    group.add_argument('-test', '--run_test', \
                        action="store_true", default=False, \
                        help="Test query to verify presence of data.")
    group.add_argument('-indices', '--get_indices', action="store_true", \
                       default=False, help="Get summary of indices.")
    
    # Extensions
    parser.add_argument('-tdf_ext', '--tdf_extensions', nargs='+', \
                        default=default_tdf_extensions, \
                        help="TDF file extensions to process when processing an \
                              entire directory.  If not specified, defaults \
                              to " + default_tdf_extensions_string)
    parser.add_argument('-map_ext', '--map_extensions', nargs='+', \
                        default=default_map_extensions, \
                        help="Map file extensions to process when processing an \
                              entire directory.  If not specified, defaults \
                              to " + default_map_extensions_string)
    parser.add_argument('-fn_ext', '--field_name_translations_extensions', \
                        nargs='+', default=None, \
                        help="Extensions of files containing field name \
                              translations.  If not specified, no attempt at \
                              changing field names will be made.")
    
    parser.add_argument('-s', '--es_server', nargs=1, required=True, \
                        help="The ElasticSearch database's server and port.")
    parser.add_argument('-del', '--delete_preexisting_index', \
                        action="store_true", default=False, \
                        help="Before adding docs to an index, delete the index \
                              if it already exists.")

    parser.add_argument('-map', '--map_file_path', nargs=1, default=None, \
                        help="Path to file containing the desired mapping for \
                              this index.")
    parser.add_argument('-fn', '--field_name_translations_path', nargs=1, \
                        default=None, \
                        help="Path to file containing field name translations \
                              for this index.")
    
    parser.add_argument('-user', '--username', nargs=1, default=None, \
                        help="Username for ElasticSearch database.")
    parser.add_argument('-pass', '--password', nargs=1, default=None, \
                        help="Password for ElasticSearch database.")

    return parser.parse_args()



#
# The main method.
#
def main(argv):
    args = set_up_argparser()

    operation_start_time = time.time()

    # Construct user-friendly summary of operations run
    friendly_list_of_ops = []
    
    # args.es_server only allows a SINGLE argument at present (05/2013)
    # but is still parsed in by argparser as a single-item list.  Since
    # it's used in multiple places below, let's assign that single item
    # to a variable for convenience.
    es_server = args.es_server[0]
    
    # by setting this to None, we can pass the variable into the ES
    # connection method regardless of whether there's any basic auth data and 
    es_basic_auth = None
    
    if args.username is not None and args.password is not None:
        es_basic_auth = { 'username': args.username,
                          'password': args.password }

    if args.files is not None:
        for f in args.files:
            add_tdf_to_elasticsearch(f, es_server, \
                    delete_preexisting_index=args.delete_preexisting_index, \
                    mapping=args.map_file_path[0], \
                    field_translations=args.field_name_translations_path[0], \
                    es_basic_auth=es_basic_auth)
        
        friendly_list_of_ops.append("adding " + str(len(args.files)) + \
                                    " file(s) to the ElasticSearch database")

    if args.dirs is not None:
        files_converted = 0
        for d in args.dirs:
            files_converted += add_tdfs_in_dir_to_elasticsearch(d, \
                    es_server, tdf_extensions=args.tdf_extensions, \
                    field_translations_extensions=args.field_name_translations_extensions, \
                    es_basic_auth=es_basic_auth, \
                    delete_preexisting_indices=args.delete_preexisting_index)

        friendly_list_of_ops.append("adding " + str(files_converted) + \
                " files in " + str(len(args.dirs)) + " directories to the \
                 ElasticSearch database")

    if args.run_test == True:
        test_es(es_server, es_basic_auth=es_basic_auth)
        friendly_list_of_ops.append("running a test query on the ES database")

    if args.get_indices == True:
        print pyes.ES(es_server).get_indices()

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
