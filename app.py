from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

import json
from elasticsearch import Elasticsearch
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')


# URL = 'https://zenodo.org/oai2d?verb=ListRecords&set=user-actionprojecteu'
URL = config.get('elasticsearch', 'url')

es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

def init(user):
	fullURL=URL+user
	registry = MetadataRegistry()
	registry.registerReader('oai_dc', oai_dc_reader)
	client = Client(fullURL, registry)
	return(client)


def record(community, user):
	client=init(user)
	for record in client.listRecords(metadataPrefix='oai_dc'):
		# print("Headers")
		# print(record[0].identifier())
		# print(record[0].datestamp())
		# print(record[0].setSpec())
		# print(record[0].isDeleted())

		# print("\nMetadata")
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
		print(identifier[0])

		# res = es.search(index="prueba", body={"query": {"match": {"title": title[0], "creator":creator[0]}}})
		if es.indices.exists(index=community):
			res = es.search(index=community, body={"query": {"bool": {"should": [{"match": {"identifier": identifier[0]}}]}}})
			print(res['hits']['total']['value'])
			if res['hits']['total']['value'] == 0:
				es.index(index=community, body=r)
		else:
			es.index(index=community, body=r)




def main():
	communities = config.items( "communities" )
	for community, user in communities:
		record(community, user)


if __name__ == "__main__":
    main()