# %%
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# %%
url='https://www.cpc.gov.mo/api/news/list'
headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
r=requests.get(url, headers=headers)

# %%
data=r.json()['data']
restructured_posts=[]
domain='https://www.cpc.gov.mo/'


if data.get('list'):
    for post in data['list']:
        title=post['title']
        if post.get('url'):
            link=domain+post['url']
        else:
            link=''
        date=post['dateAt']
        # date=datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d %H:%M:%S')
        if post.get('content'):
            content=BeautifulSoup(BeautifulSoup(post['content'], 'html.parser').decode('utf-8')).text
        else:
            content=''
        dict_post={
                'title': title,
                'link': link,
                'date': date,
                'content': content
            }
        restructured_posts.append(dict_post)

    # %% [markdown]
    # 

    # %%

    import xml.etree.ElementTree as ET

    # Create the root of the RSS feed
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    # Add channel elements
    ET.SubElement(channel, 'title').text = 'Comissão Profissional dos Contabilistas Notícias'
    ET.SubElement(channel, 'link').text = url
    ET.SubElement(channel, 'description').text = 'CPC RSS'

    # Add items
    for item in restructured_posts:
        item_elem = ET.SubElement(channel, 'item')
        ET.SubElement(item_elem, 'title').text = item['title']
        ET.SubElement(item_elem, 'link').text = item['link']
        ET.SubElement(item_elem, 'description').text = item['content']
        ET.SubElement(item_elem, 'pubDate').text = item['date']

    # Convert to string and save to an XML file
    rss_feed = ET.tostring(rss, encoding='utf-8', method='xml').decode()
    with open('CPC.xml', 'w', encoding='utf-8') as xml_file:
        xml_file.write(rss_feed)

