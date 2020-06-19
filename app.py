from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

import json
from datetime import datetime

from elasticsearch import Elasticsearch
from configparser import ConfigParser

from influxdb import InfluxDBClient

from bs4 import BeautifulSoup
import urllib.request

import logging

config = ConfigParser()
config.read('config.ini')

#clientInflux = InfluxDBClient(host='localhost', port=8086)
clientInflux = InfluxDBClient('192.168.123.245', '8086', 'action', 'admin@ct1on')

URL = config.get('zenodo', 'url')

es = Elasticsearch(hosts=config.get('elasticsearch', 'url'))

logging.basicConfig(filename='log/'+str(datetime.now().date())+'.log', filemode='w', level=logging.INFO
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
	views = 0
	downloads = 0
	documents = 0
	for record in client.listRecords(metadataPrefix='oai_dc'):

		documents += 1
		dic = record[1].getMap()
		dic['datestamp'] = str(record[0].datestamp())
		identifier = dic['identifier'][0].split("/")[-1]
		statistics = webscrapping(identifier)
		dic['views'] = statistics[0]
		views += int(statistics[0].replace(',',''))
		dic['downloads'] = statistics[1]
		downloads += int(statistics[1].replace(',',''))
		dic['id'] = identifier.split("/")[-1]
		r = json.dumps(dic, indent=4, sort_keys=True)

		insertElactic(community, identifier, r)
		insertInflux(community, identifier, views, downloads)
	insertElacticCommunity(community, views, downloads, documents)
	insertInfluxCommunity(community, views, downloads, documents)


def insertInfluxCommunity(community, views, downloads, documents):
	json_body = [{
			"measurement": "statistics",
	        "tags": {
	            "id": community,
	            "community": 'communities' },
	        "time": str(datetime.now()),
	        "fields": {
	            "views": views,
	            "downloads": downloads,
	            "documents": documents
	        }
	    }]
	res = clientInflux.write_points(json_body)
	logging.info('The community %s saved properly in influxdb with response: %s', community, res)

def insertInflux(community, identifier, views, downloads):
	json_body = [{
			"measurement": "statistics",
	        "tags": {
	            "id": identifier,
	            "community": community },
	        "time": str(datetime.now()),
	        "fields": {
	            "views": views,
	            "downloads": downloads
	        }
	    }]
	res = clientInflux.write_points(json_body)
	logging.info('File %s of the community %s saved properly in influxdb with response: %s', identifier, community, res)


def insertElacticCommunity(community, views, downloads, documents):
	r = {
	    'community': community,
	    'views': views,
	    'downloads': downloads,
	    'documents': documents,
	    'time': str(datetime.now())
	}
	if es.indices.exists(index='communities'):
		res = es.search(index='communities', body={"query": {"query_string": {"query": 'community'+':'+community}}})
		if res['hits']['total']['value'] == 0:
			response = es.index(index='communities', body=r)
			logging.info('Community %s created with %s views, %s downloads', community, views, downloads)
		elif res['hits']['total']['value'] == 1:
			response = es.index(index='communities', id=res['hits']['hits'][0]['_id'], body=r)
			logging.info('Community %s updated with %s views, %s downloads', community, views, downloads)
		else:
			logging.error("Error, multiple resources found for %s", community)
	else:
		response = es.index(index='communities', body=r)
		logging.info('index communities created')
		logging.info('Community %s created with %s views, %s downloads', community, views, downloads)


def insertElactic(community, identifier, r):
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
		logging.info('index %s created', community)
		logging.info('%s created', identifier)
	logging.info('From %s the file %s saved properly', community, identifier)


def webscrapping(identifier):
	webpage = "https://zenodo.org/record/" + identifier
	websource = urllib.request.urlopen(webpage)
	soup = BeautifulSoup(websource.read(), "html.parser")

	views = soup.find('span',{'class':'stats-data'}).text
	downloads = soup.find('span',{'class':'stats-data'}).find_next('span').text
	return [views,downloads]



def main():
	logging.info('The harvester starts')
	clientInflux.create_database('dataportal')
	clientInflux.switch_database('dataportal')
	communities = config.items("communities")
	for community, user in communities:
		record(community, user)
	logging.info('The harvester finishes')


if __name__ == "__main__":
    main()
