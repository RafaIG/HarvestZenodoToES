# ODP_ZenodoHarvester


## What is it?
ODP_ZenodoHarvester is a Python project to harvest the [Zenodo's](https://zenodo.org/) resources and statistics for [ACTION](https://actionproject.eu/). This data is saved in Elasticsearch and in InfluxDB and will be used in the [open data portal](https://github.com/actionprojecteu/ODP_frontend).


## Files

The project files in order are:
 - [log](log/) : is the folder in which the logs will be placed.
 - [Dockerfile](Dockerfile) : file for dockerize the api.
 - [README](README) : contains the description and relevant information.
 - [app.py](app.py) : is the python program file.
 - [config.ini](config.ini) : contains the project importance settings (e.g. the communities).
 - [requirements.txt](requirements.txt) : the libraries needed for the proper operation for app.py.


## Dockerize and scheduler the application

Before Dockeryze the aplication, you need to download the project (e.g. `git pull` ). Then, to create the image, execute the following command in the project folder:

`sudo docker build -t harvester .`

Finally, to run the image with docker:

`docker run --name myharvester --network host -v /var/log/harvestZenodo:/opt/log -d harvester`

The above command map the log folder of the docker with the folder of the host machine `/var/log/harvestZenodo`, that could be change at will. It also shares the host's network, making it easier to communicate with Elasticsearch.

Once we create it, to run it every day (e.g. at 1 AM), we need to start and erase the image periodically. So, we will using crontab. We courd edit crontab with:

`crontab -e`

And add at the end:
```
55 1 * * * ubuntu  sudo /usr/bin/docker rm -f myharvester
0 1 * * * ubuntu  sudo /usr/bin/docker run --name myharvester --network host -v /var/log/harvestZenodo:/opt/log -d harvester
```

## Components

### Zenodo

The [app.py](app.py) program file connects to Zenodo and harvest the oai_dc of the resources (in the **init** function). We create a oai_dc client for each community and process every record individually (**record**). The record data that is extracted contains: title, author, description , lenguage, and so on. Additionally, web scraping is used in order to get the statistical data, like downloads and views of each resource.

### Elasticsearch

In the **record** function, we add to the resource data: the harvest date, the number of visits and the number of downloads. We save the new record in its community index in Elasticsearch (**insertElactic**). Finnally, we update the index *communities* of Elasticsearch with the number of documents, views and download for the entire community (**insertElacticCommunity**).

### InfluxDB

InfluxDB helps keep track of views and downloads for the communities. We use the function **insertInflux** to add data from a resource and **insertInfluxCommunity** to add the statistics of an entire community. We track the number of downloads and views and save them in the table *dataportal* of an InfluxDB database.

### Logging

All the process is tracked in a log, that is created every day (e.g. 2020-04-21.log  2020-04-27.log) in the [log](log/) folder.


## Configuration and dependencies

The [config.ini](config.ini)  is the configuration file of the program. It contains the URL of Zenodo and Elasticsearch and the Zenodo's communities that will be harvested:
 - action
 - sonickayak
 - street-spectra
 - students-and-air-pollution

The [requirements.txt](requirements.txt) contains the python libraries needed for the proper operation of the program. They could be installed by:

´pip install -r requirements.txt´


## Appendix I: configure Elasticsearch

In first place, install Elasticsearch:
```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt -y install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
```


For security, enable the xpack plugin, that comes with the default installation. In the ´/etc/elasticsearch/elasticsearch.yml´ file, change in the end:
```
xpack.security.enabled: true


xpack.security.authc:
  anonymous:
    username: anonymous_user
    roles: watcher_user,only_get
    authz_exception: true
```

And in the same file, change the network configuration:
```
network.host: 0.0.0.0
transport.host: 127.0.0.1
http.port: 9200
```

Now, it is require to create a password for elasticsearch:

`/usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive`

And create an anonymous user that could search in the differents index of Elasticsearch from outside the host machine:
```
curl -XPUT -u elastic:3st3ban localhost:9200/_security/role/only_get --header 'Content-Type: application/json' -d '
{
	"run_as": [ "anonymous_user" ],
	"indices": [
	{
		"names": [ "*" ],
		"privileges": [ "read" ]
	}
	]
}
'
```
