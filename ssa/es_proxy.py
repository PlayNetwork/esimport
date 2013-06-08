import sys

import rawes



#
# Removes all documents in ES for specified index and type
# http://www.elasticsearch.org/guide/reference/api/admin-indices-delete-mapping/
#
def clear_documents(index_name, type_name, es):
	path = index_name + "/" + type_name
	try:
		return es.delete(path)
	except Exception as e:
		# ES returns 404 when resource is not found
		if hasattr(e, 'status_code') and e.status_code == 404:
			return "index or type did not previously exist"
		raise e



#
# Creates an index in ES by specified name if one does not already exist
# http://www.elasticsearch.org/guide/reference/api/admin-indices-create-index/
#
def ensure_index(index_name, es):
	try:
		return es.put(index_name)
	except Exception as e:
		# ES returns generic 400 when index already exists
		if hasattr(e, 'status_code') and e.status_code == 400:
			return "index exists"
		raise e



#
# Creates a mapping with the specified index and type
# http://www.elasticsearch.org/guide/reference/api/admin-indices-put-mapping/
#
def ensure_mapping(index_name, type_name, mapping, es):
	path = index_name + "/" + type_name + "/_mapping"
	return es.put(path, data=mapping)



#
# Creates a "connection" to ES with specified username and password
# https://github.com/humangeo/rawes#usage
#
def get_es(es_server, username, password):
	return rawes.Elastic(es_server, auth=(username, password), verify=False)



def bulk_index_doc(docs, index_name, type_name, es):
	path = index_name + "/" + type_name + "/_bulk?refresh=true"
	return es.post(path, data=docs)


#
# Adds a new document to ES, uses POST to auto-generate an ID
# http://www.elasticsearch.org/guide/reference/api/index_/
#
def index_doc(doc, index_name, type_name, es):
	path = index_name + "/" + type_name + "/"
	return es.post(path, data=doc)
