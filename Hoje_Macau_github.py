# %%
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

# %%
today = (datetime.today()-timedelta(days=1)).strftime('%Y/%m/%d')
today = (datetime.today()).strftime('%Y/%m/%d')
url=f'https://hojemacau.com.mo/{today}/'
headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
r=requests.get(url, headers=headers)
r

# %%
soup=BeautifulSoup(r.content, "html.parser")


lst_post=soup.find_all('h2', {'class': re.compile('entry-title')})


# %%
def get_article(url):
    headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
    r=requests.get(url, headers=headers)
    soup=BeautifulSoup(r.content, "html.parser")

    if soup.find('time', {'class': re.compile('entry-date')}):
        date=soup.find('time', {'class': re.compile('entry-date')}).get('datetime')
        date=datetime.fromisoformat(date).strftime('%Y-%m-%d %H:%M:%S')
    else:
        date=None
        
    if soup.find('div', {'class': 'entry-content'}):
        content=soup.find('div', {'class': 'entry-content'}).text
    else:
        content=None

    if soup.find('a', {'rel': re.compile('category tag')}):
        cat=soup.find('a', {'rel': re.compile('category tag')}).text.strip()
    else:
        cat=None

    if soup.find('a', {'class': re.compile('author')}):
        author=soup.find('a', {'class': re.compile('author')}).text.strip()
    else:
        author=None
    
    return date, content,cat, author


if lst_post:
    restructured_posts=[]
    for idx, post in enumerate(lst_post):
        
        title=post.a.text
        link=post.a.get('href')
        date, content,cat, author=get_article(link)

        dict_post={
            'title': title,
            'category': cat,
            'author': author,
            'link': link,
            'date': date,
            'content': content
        }
        restructured_posts.append(dict_post)

    # %%
    import xml.etree.ElementTree as ET

    # Create the root of the RSS feed
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    # Add channel elements
    ET.SubElement(channel, 'title').text = 'Hoje Macau'
    ET.SubElement(channel, 'link').text = url
    ET.SubElement(channel, 'description').text = 'Hoje Macau RSS'

    # Add items
    for item in restructured_posts:
        item_elem = ET.SubElement(channel, 'item')
        ET.SubElement(item_elem, 'title').text = item['title']
        ET.SubElement(item_elem, 'link').text = item['link']
        
        # If using BeautifulSoup, it's safer to use .decode_contents() for HTML 
        # or .get_text() for plain text.
        content = item['content']
        ET.SubElement(item_elem, 'description').text = content
        
        ET.SubElement(item_elem, 'pubDate').text = item['date']

    # Convert to string and save to an XML file
    rss_feed = ET.tostring(rss, encoding='utf-8', method='xml').decode()
    with open('Hoje_Macau.xml', 'w', encoding='utf-8') as xml_file:
        xml_file.write(rss_feed)

