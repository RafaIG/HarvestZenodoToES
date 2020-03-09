from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

import json
from elasticsearch import Elasticsearch
from configparser import ConfigParser

from bs4 import BeautifulSoup
import urllib.request

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
		identifier = dic['identifier'][0].split("/")[-1]
		statistics = webscrapping(identifier)
		dic['views'] = statistics[0]
		dic['downloads'] = statistics[1]
		dic['id'] = identifier.split("/")[-1]
		r = json.dumps(dic, indent=4, sort_keys=True)

		print(identifier)

		# res = es.search(index="prueba", body={"query": {"match": {"title": title[0], "creator":creator[0]}}})
		if es.indices.exists(index=community):
			res = es.search(index=community, body={"query": {"term": {"id": identifier}}})
			print("Documents found", res['hits']['total']['value'])
			if res['hits']['total']['value'] == 0:
				response = es.index(index=community, body=r)
				print(response['result'])
			elif res['hits']['total']['value'] == 1:
				response = es.index(index=community, id=res['hits']['hits'][0]['_id'], body=r)
				print(response['result'])
			else:
				print("Error, multiple resources found with the id", identifier)
		else:
			response = es.index(index=community, body=r)
			print(response['result'])


def webscrapping(identifier):
	webpage = "https://zenodo.org/record/" + identifier
	websource = urllib.request.urlopen(webpage)
	soup = BeautifulSoup(websource.read(), "html.parser")

	views = soup.find('span',{'class':'stats-data'}).text
	downloads = soup.find('span',{'class':'stats-data'}).find_next('span').text
	return [views,downloads]



def main():
	communities = config.items( "communities" )
	for community, user in communities:
		record(community, user)


if __name__ == "__main__":
    main()