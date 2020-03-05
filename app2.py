from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
import oaipmh

import json
from elasticsearch import Elasticsearch



URL = 'https://zenodo.org/oai2d?verb=ListRecords&set=user-actionprojecteu'

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

def init():
	registry = MetadataRegistry()
	registry.registerReader('oai_dc', oai_dc_reader)
	client = Client(URL, registry)
	return(client)


def record(client):
	for record in client.listRecords(metadataPrefix='oai_dc'):
		# print("Headers")
		# print(record[0].identifier())
		# print(record[0].datestamp())
		# print(record[0].setSpec())
		# print(record[0].isDeleted())

		print("\nMetadata")
		dic = record[1].getMap()
		dic['datestamp'] = str(record[0].datestamp())
		r = json.dumps(dic, indent=4, sort_keys=True)
		# print(r)
		title = record[1]["title"]
		creator = record[1]["creator"]
		date = record[1]["date"]
		contributor = record[1]["contributor"]
		rights = record[1]["rights"]
		description = record[1]["description"]
		identifier = record[1]["identifier"]
		language = record[1]["language"]
		relation = record[1]["relation"]
		subject = record[1]["subject"]
		type = record[1]["type"]

		# res = es.search(index="prueba", body={"query": {"match": {"title": title[0], "creator":creator[0]}}})
		if es.indices.exists(index="prueba"):
			res = es.search(index="prueba", body={"query": {"bool": {"should": [{"match": {"identifier": identifier[0]}}]}}})
			print(res['hits']['total']['value'])
			if res['hits']['total']['value'] == 0:
				es.index(index='prueba', body=r)
		else:
			es.index(index='prueba', body=r)


		print("\n \n \n")


		#  print(record[2])




def main():
	client=init()
	record(client)


if __name__ == "__main__":
    main()