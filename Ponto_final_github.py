# %%
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
from email.utils import formatdate # 用嚟整標準 RSS 時間格式
import logging

# 基本設定
logging.basicConfig(
    level=logging.INFO, # 設定顯示邊個等級以上嘅訊息
    format='%(asctime)s - %(levelname)s - %(message)s', # 設定格式：時間 - 等級 - 內容
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("news.log", encoding='utf-8'), # 儲存到檔案
        logging.StreamHandler() # 同時噴喺 Console
    ]
)
# %%

today = (datetime.today()).strftime('%Y/%m/%d')
logging.info(f"🚀 爬取《Ponto Final》程式啟動。目前設定日期: {today}。")
url=f'https://pontofinal-macau.com/{today}/'
headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
r=requests.get(url, headers=headers)
time.sleep(2)

# %%
if r.status_code==200:
    soup=BeautifulSoup(r.content, "html.parser")
    
    content_tag=soup.find_all('div', class_='td-main-content-wrap td-container-wrap')
    if content_tag:
        content=content_tag[0]
        posts=content.find_all('h3', class_='entry-title td-module-title')
        valid_post=list(set([post.find_all('a')[0].get('href') for post in posts]))
    else:
        valid_post=[]
    total_no_post=len(valid_post)
    logging.info(f"成功獲取 {today} 數據，當日有{total_no_post}條新聞。")
    # print(f'Ponto Final {today} 日有{len(valid_post)}條新聞')
else:
    logging.error(f"❌ {today} 連線失敗: {r.status_code}")

# %%
def get_article(url):
    headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
    r=requests.get(url, headers=headers)
    time.sleep(10)
    soup=BeautifulSoup(r.content, "html.parser")

    # data=soup.find_all('div', {'class': 'td-pb-span8'})[-1]
    if soup.find('time', {'class': 'entry-date updated td-module-date'}):
        date_str=soup.find_all('time', {'class': 'entry-date updated td-module-date'})[0].get('datetime')
        dt=datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
        date = formatdate(time.mktime(dt.timetuple()))
    else:
        date = formatdate() # 萬一冇日期就用而家

    img_url = ""
    img_tag = soup.find('img', {'class': re.compile('entry-thumb')})
    if img_tag:
        img_url = img_tag.get('src')
    
    if soup.find('h1', class_='tdb-title-text'):
        title=soup.find_all('h1', class_='tdb-title-text')[0].get_text().strip()
    else:
        title=None

    if soup.find('a', {'class': 'tdb-author-name'}):
        author=soup.find_all('a', {'class': 'tdb-author-name'})[0].get_text().strip()
    else:
        author=None

    if soup.find('div', class_='td-post-content'):
        # content=soup.find_all('div', class_='td-post-content')[0].get_text().strip()
        content=soup.find_all('div', class_='td-post-content')[0].decode_contents()

        if img_url:
            content = f'<img src="{img_url}" style="width:100%; margin-bottom:10px;""")/>><br/>' + content
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
        logging.info(f"正在爬取{idx+1}/{total_no_post}則新聞。")
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
        logging.info(f"✅ 成功獲取: {title}。")
        time.sleep(1.5) # 每次入內文前停一停，對人哋 Server 禮貌

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
    xml_file_name='Ponto_final_pt.xml'
    with open(xml_file_name, 'w', encoding='utf-8') as xml_file:
        xml_file.write(rss_feed)
    logging.info(f"✅ 成功保存: {xml_file_name}。")
else:
    logging.info("⚠️ 當日沒有新聞。")
