from bs4 import BeautifulSoup
import urllib.request

webpage = "https://zenodo.org/record/3690549"

websource = urllib.request.urlopen(webpage)
soup = BeautifulSoup(websource.read(), "html.parser")

# t=soup.find('span',{'class':'stats-data'})
#cosa = soup.find("div", {"class": "stats-data"}).span.content
# print(t)

print(soup.find('span',{'class':'stats-data'}).text)

print(soup.find('span',{'class':'stats-data'}).find_next('span').text)

