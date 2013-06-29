import json
import sys

import rawes



TIMEOUT_DEFAULT = 60



class ElasticSearchConnection:
	#
	# Creates a "connection" to ES with specified username and password
	# https://github.com/humangeo/rawes#usage
	#
	def __init__(self, server, username, password, timeout=TIMEOUT_DEFAULT, verify=True):
		self.es = rawes.Elastic(server, auth=(username, password), timeout=timeout, verify=verify)



	#
	# Removes all documents in ES for specified index and type
	# http://www.elasticsearch.org/guide/reference/api/admin-indices-delete-mapping/
	#
	def clear_documents(self, index_name, type_name):
		path = index_name + "/" + type_name
		try:
			return self.es.delete(path)
		except Exception as e:
			# ES returns 404 when resource is not found
			if hasattr(e, 'status_code') and e.status_code == 404:
				return "index or type did not previously exist"
			raise e



	#
	# Creates an index in ES by specified name if one does not already exist
	# http://www.elasticsearch.org/guide/reference/api/admin-indices-create-index/
	#
	def ensure_index(self, index_name):
		try:
			return self.es.put(index_name)
		except Exception as e:
			# ES returns generic 400 when index already exists
			if hasattr(e, 'status_code') and e.status_code == 400:
				return "index exists"
			raise e



	#
	# Creates a mapping with the specified index and type
	# http://www.elasticsearch.org/guide/reference/api/admin-indices-put-mapping/
	#
	def ensure_mapping(self, index_name, type_name, mapping):
		path = index_name + "/" + type_name + "/_mapping"
		return self.es.put(path, data=mapping)



	#
	# Persists a Dictionary in ES via bulk index API
	# http://www.elasticsearch.org/guide/reference/api/bulk/
	#
	def bulk_index_docs(self, iterable, index_name, type_name, chunk_size, show_status=None):
		path = index_name + "/" + type_name + "/_bulk"

		# For bulk ES insert, a command must be present above every data document
		# that specifies the action to perform. This generator inserts the index
		# command into an iterable at the appropriate locations.
		def bulk_index_generator(it):
			for d in it:
				yield dict(index=dict(_index=index_name, _type=type_name))
				yield d

		docs = [json.dumps(doc) for doc in bulk_index_generator(iterable)]
		for i in range(0, len(docs), chunk_size):
			data="\n".join(docs[i:i + chunk_size]) + "\n"
			self.es.post(path, data=data)

			if show_status is not None:
				show_status(i + chunk_size, len(docs))

		return "POST " + path + " complete"



	#
	# Adds a new document to ES, uses POST to auto-generate an ID
	# http://www.elasticsearch.org/guide/reference/api/index_/
	#
	def index_doc(self, doc, index_name, type_name):
		path = index_name + "/" + type_name + "/"
		return self.es.post(path, data=doc)
