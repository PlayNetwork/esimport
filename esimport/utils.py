import sys



#
# Opens a file and returns its contents as a string after
# encoding to UTF-8
#
def retrieve_file(filename):
	with open(filename, 'rb') as f:
		original_contents = f.read()

	decoded_contents = original_contents.decode('utf-8-sig').encode('utf-8')
	return decoded_contents



#
# Opens a file and returns its contents as an List of lines
# after encoding to UTF-8
#
def retrieve_file_lines(filename):
	decoded_contents = retrieve_file(filename)

	return decoded_contents.splitlines()
