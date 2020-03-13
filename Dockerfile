FROM python:3.8
ADD . ./opt/
WORKDIR /opt/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python","app.py"]

# sudo docker build -t harvester .
# docker run --name myharvester -v /var/log/harvestZenodo:/opt/log -d harvester
