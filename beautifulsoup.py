import requests
from bs4 import BeautifulSoup
url = 'https://tenor.com/view/hideri-hideri-kanzaki-hideri-hanzaki-anime-hug-hug-gif-21152269'
response = requests.get(url)
soup = BeautifulSoup(response.text)
metas = soup.find_all(property='og:url')

for meta in metas:
    print(type(meta.attrs.get("content")))

    