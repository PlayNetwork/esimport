import sys
import csv
import json
import time
import os
import argparse



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



def tdf_to_json (filename):
    method_start_time = time.time()

    remove_bom_from_utf8(filename)

    with open(filename, 'rb') as tdf:
        sys.stdout.write("Reading in TDF... ")  # print next info on same line
        sys.stdout.flush()

        start_time = time.time()

        reader = csv.DictReader(tdf, delimiter='\t')
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


def main(argv):
    default_input_extensions = ['.txt']
    default_extensions_string = ""

    for extension in default_input_extensions:
        default_extensions_string += extension
        if extension is not default_input_extensions[-1]:
            if len(default_input_extensions) > 1:
                default_extensions_string += "; "

    #
    # Set up arg parser
    #
    parser = argparse.ArgumentParser(description='Process TDF files.')
    parser.add_argument('-ext', '--input_extensions', nargs=1, \
                       default=default_input_extensions, \
                       help="")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--files', nargs='+', \
                       help="TDF files that need to be converted to \
                             JSON-format files.")
    group.add_argument('-p', '--paths', nargs='+', \
                       help="Directories containing TDF files that need to be \
                             converted to JSON-format files.  Default \
                             extension(s) if not specified with '-ext': " + \
                             default_extensions_string)

    args = parser.parse_args()
    #
    # End of setting up arg parser
    #

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

        print operation_description.capitalize() + " took " + \
              str(operation_elapsed_time) + " seconds."




if __name__ == "__main__":
    main(sys.argv[1:])
