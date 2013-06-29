# Python dependencies
import csv
import json
import math
import os
import sys
import time

# local source dependencies
from elasticsearch import ElasticSearchConnection
import utils



BULKINDEX_COUNT = 1000
DELIMITER_DEFAULT = ","
SERVER_DEFAULT = "localhost:9200"



#
# Index the contents of a CSV file into ElasticSearch
#
def import_data(filename, \
	index_name, \
	type_name, \
	delimiter, \
	server, \
	delete_type=False, \
	field_translations=None, \
	mapping=None, \
	username=None, \
	password=None, \
	bulk_index_count=BULKINDEX_COUNT, \
	timeout=None, \
	verify=True):

	if server is None:
		server = SERVER_DEFAULT

	if bulk_index_count is None:
		bulk_index_count = BULKINDEX_COUNT

	data_lines = utils.retrieve_file_lines(filename)

	if len(data_lines) < 2:
		print "there is no data to import in " + filename
		return

	es = ElasticSearchConnection(server, username, password, timeout, verify)
	full_url = server + "/" + index_name + "/" + type_name

	if delete_type:
		print "clearing existing documents from " + full_url
		es.clear_documents(index_name, type_name)

	if es.ensure_index(index_name):
		if mapping is not None:
			print "applying mapping from " + mapping + " to " + full_url
			try:
				mapping_def = json.loads(utils.retrieve_file(mapping))
				es.ensure_mapping(index_name, type_name, mapping_def)
			except ValueError:
				print "supplied JSON was not formatted correctly, skipping this step"

		start_time = time.time()

		# ensure large fields can be parsed
		csv.field_size_limit(sys.maxsize)

		# translate field names if applicable
		if field_translations is not None:
			reader = translate_fields_reader(data_lines, field_translations, delimiter)
		else:
			reader = csv.DictReader(data_lines, delimiter=delimiter)

		# closure for displaying status of operation
		def show_status(current_count, total_count):
			percent_complete = current_count * 100 / total_count
			sys.stdout.write("\rstatus: %d%%" % percent_complete)
			sys.stdout.flush()

		print "importing data into " + full_url + " (" + str(bulk_index_count) + " rows at a time) from file " + filename
		es.bulk_index_docs(reader, \
			index_name, \
			type_name, \
			bulk_index_count, \
			show_status)

		# indicate completion
		show_status(100, 100)
		end_time = time.time() - start_time
		print ", operation completed in %.2f seconds" % end_time

	else:
		print "index at " + server + "/" + index_name + " can't be written to"

	return



#
# Returns iterable with new field names based on the instructions in a
# CSV field translations file.
#
def translate_fields_reader(data_lines, field_translations_path, delimiter):
	reader = csv.DictReader(data_lines, delimiter=delimiter)
	fieldtranslation_lines = utils.retrieve_file_lines(field_translations_path)

	if len(fieldtranslation_lines) < 2:
		return reader

	original_keys = data_lines[0]
	fieldname_keys = fieldtranslation_lines[0].split(delimiter)
	fieldname_values = fieldtranslation_lines[1].split(delimiter)

	# Filters the fields within a Dictionary and maps them to the specified
	# fieldvalue names so that only fields specified in the field translations
	# document are returned
	def field_filter(it, keys, fieldvalues):
		for d in it:
			yield dict((fieldvalues[keys.index(k)], d[k]) for k in keys if k in original_keys and k != "")

	return field_filter(reader, fieldname_keys, fieldname_values)
