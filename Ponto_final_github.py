# %%
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time

# %%
# today = datetime.today().strftime('%Y/%m/%d')
today = (datetime.today()-timedelta(days=1)).strftime('%Y/%m/%d')
today = (datetime.today()).strftime('%Y/%m/%d')
url=f'https://pontofinal-macau.com/{today}/'
headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
r=requests.get(url, headers=headers)
time.sleep(10)
r

# %%
soup=BeautifulSoup(r.content, "html.parser")

content=soup.find_all('div', class_='td-main-content-wrap td-container-wrap')[0]
posts=content.find_all('h3', class_='entry-title td-module-title')
valid_post=list(set([post.find_all('a')[0].get('href') for post in posts]))


# %%
def get_article(url):
    headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
    r=requests.get(url, headers=headers)
    time.sleep(10)
    soup=BeautifulSoup(r.content, "html.parser")

    # data=soup.find_all('div', {'class': 'td-pb-span8'})[-1]
    if soup.find('time', {'class': 'entry-date updated td-module-date'}):
        date=soup.find_all('time', {'class': 'entry-date updated td-module-date'})[0].get('datetime')
        date=datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S')
    else:
        date=None
    
    if soup.find('h1', class_='tdb-title-text'):
        title=soup.find_all('h1', class_='tdb-title-text')[0].get_text().strip()
    else:
        title=None

    if soup.find('a', {'class': 'tdb-author-name'}):
        author=soup.find_all('a', {'class': 'tdb-author-name'})[0].get_text().strip()
    else:
        author=None

    if soup.find('div', class_='td-post-content'):
        content=soup.find_all('div', class_='td-post-content')[0].get_text().strip()
    else:
        content=None

    if soup.find('a', {'class': 'tdb-entry-category'}):
        cat=soup.find_all('a', {'class': 'tdb-entry-category'})[0].get_text().strip()
    else:
        cat=None

    return date, title, cat, author, content

# %%
if valid_post:
    restructured_posts=[]
    for idx, url in enumerate(valid_post):
        date, title, cat, author, content=get_article(url)
        dict_post={
            'title': title,
            'category': cat,
            'author': author,
            'link': url,
            'date': date,
            'content': content
        }
        restructured_posts.append(dict_post)

    # %%
    restructured_posts

    # %%

    import xml.etree.ElementTree as ET

    # Create the root of the RSS feed
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    # Add channel elements
    ET.SubElement(channel, 'title').text = 'Ponto_final'
    ET.SubElement(channel, 'link').text = 'https://pontofinal-macau.com'
    ET.SubElement(channel, 'description').text = 'Ponto_final RSS'

    # Add items
    for item in restructured_posts:
        item_elem = ET.SubElement(channel, 'item')
        ET.SubElement(item_elem, 'title').text = item['title']
        ET.SubElement(item_elem, 'link').text = item['link']
        ET.SubElement(item_elem, 'description').text = item['content']
        ET.SubElement(item_elem, 'pubDate').text = item['date']

    # Convert to string and save to an XML file
    rss_feed = ET.tostring(rss, encoding='utf-8', method='xml').decode()
    with open('Ponto_final_pt.xml', 'w', encoding='utf-8') as xml_file:
        xml_file.write(rss_feed)
