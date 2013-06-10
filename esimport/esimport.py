# Python dependencies
import csv
import math
import os
import sys
import time

# local source dependencies
from elasticsearch import ElasticSearch
import utils



BULKINDEX_COUNT = 1000



#
# Index the contents of a CSV file into ElasticSearch
#
def import_data(filename, \
	delimiter, \
	server, \
	index_name, \
	type_name, \
	delete_type=False, \
	field_translations=None, \
	mapping=None, \
	username=None, \
	password=None):

	data_lines = utils.retrieve_file_lines(filename)

	if len(data_lines) < 2:
		print "there is no data to import in " + filename
		return

	es = ESProxy(server, username, password)
	full_url = server + "/" + index_name + "/" + type_name

	if delete_type:
		print "clearing existing documents from " + full_url
		es.clear_documents(index_name, type_name)

	if mapping is not None:
		print "applying mapping from " + mapping + " to " + full_url
		mapping_def = utils.retrieve_file(mapping)
		es.ensure_mapping(index_name, type_name, mapping_def)

	if es.ensure_index(index_name):
		start_time = time.time()

		# translate field names if applicable
		if field_translations is not None:
			reader = translate_fields(data_lines, field_translations)
		else:
			reader = csv.DictReader(data_lines, delimiter=delimiter)

		# closure for displaying status of operation
		def show_status(current_count, total_count):
			percent_complete = current_count * 100 / total_count
			sys.stdout.write("\rstatus: %d%%" % percent_complete)
			sys.stdout.flush()

		print "importing data into " + full_url + " from file " + filename
		es.bulk_index_docs(reader, \
			index_name, \
			type_name, \
			BULKINDEX_COUNT,
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
def translate_fields(data_lines, field_translations_path):
	reader = csv.DictReader(data_lines, delimiter=delimiter)
	fieldtranslation_lines = utils.retrieve_file_lines(field_translations_path)

	if len(fieldtranslation_lines) < 2:
		return reader

	fieldname_keys = fieldtranslation_lines[0].split(delimiter)
	fieldname_values = fieldtranslation_lines[1].split(delimiter)

	# Filters the fields within a Dictionary and maps them to the specified
	# fieldvalue names so that only fields specified in the field translations
	# document are returned
	def data_filter(it, keys, fieldvalues):
		for d in it:
			yield dict((fieldvalues[keys.index(k)], d[k]) for k in keys)

	return data_filter(reader, fieldname_keys, fieldname_values)
