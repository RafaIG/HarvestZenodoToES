FROM python:3.8
ADD . ./opt/
WORKDIR /opt/
EXPOSE 5000
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python","app.py"]

# sudo docker build -t harvester .
# docker run --name myharvester -d harvester
