from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

import json
from elasticsearch import Elasticsearch
from configparser import ConfigParser

from bs4 import BeautifulSoup
import urllib.request

import logging

config = ConfigParser()
config.read('config.ini')

URL = config.get('zenodo', 'url')

es = Elasticsearch(hosts=config.get('elasticsearch', 'url'))

logging.basicConfig(filename='log/harvesterlog.log', filemode='w', level=logging.INFO
	, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logging.info('This will get logged to a file')

def init(user):
	fullURL = URL+user
	registry = MetadataRegistry()
	registry.registerReader('oai_dc', oai_dc_reader)
	client = Client(fullURL, registry)
	logging.info('The community %s harvested', user)
	return(client)


def record(community, user):
	client=init(user)
	for record in client.listRecords(metadataPrefix='oai_dc'):

		dic = record[1].getMap()
		dic['datestamp'] = str(record[0].datestamp())
		identifier = dic['identifier'][0].split("/")[-1]
		statistics = webscrapping(identifier)
		dic['views'] = statistics[0]
		dic['downloads'] = statistics[1]
		dic['id'] = identifier.split("/")[-1]
		r = json.dumps(dic, indent=4, sort_keys=True)

		if es.indices.exists(index=community):
			res = es.search(index=community, body={"query": {"term": {"id": identifier}}})
			if res['hits']['total']['value'] == 0:
				response = es.index(index=community, body=r)
				logging.info('%s created',identifier)
			elif res['hits']['total']['value'] == 1:
				response = es.index(index=community, id=res['hits']['hits'][0]['_id'], body=r)
				logging.info('%s updated',identifier)
			else:
				logging.error("Error, multiple resources found with the id %s", identifier)
		else:
			response = es.index(index=community, body=r)
			logging.info('indes %s created', community)
			logging.info('%s created',identifier)

	logging.info('From %s the file %s saved properly', user, identifier)


def webscrapping(identifier):
	webpage = "https://zenodo.org/record/" + identifier
	websource = urllib.request.urlopen(webpage)
	soup = BeautifulSoup(websource.read(), "html.parser")

	views = soup.find('span',{'class':'stats-data'}).text
	downloads = soup.find('span',{'class':'stats-data'}).find_next('span').text
	return [views,downloads]



def main():
	logging.info('The harvester starts')
	communities = config.items( "communities" )
	for community, user in communities:
		record(community, user)
	logging.info('The harvester finishes')


if __name__ == "__main__":
    main()