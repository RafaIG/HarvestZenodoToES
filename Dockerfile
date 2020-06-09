FROM python:3.8
ADD . ./opt/
WORKDIR /opt/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python","app.py"]

# sudo docker build -t harvester .
# sudo docker run --name myharvester --network host -v /var/log/harvestZenodo:/opt/log -d harvester

# 55 1 * * * ubuntu  sudo /usr/bin/docker rm -f myharvester
# 0 1 * * * ubuntu  sudo /usr/bin/docker run --name myharvester --network host -v /var/log/harvestZenodo:/opt/log -d harvester
