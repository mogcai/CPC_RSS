# %%
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from email.utils import formatdate # 用嚟整標準 RSS 時間格式
import time
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
today = (datetime.today()-timedelta(days=1)).strftime('%Y/%m/%d')
today = (datetime.today()).strftime('%Y/%m/%d')

def get_jtm_post_list(page=1):
    url=f'https://jtm.com.mo/{today}/page/{page}/'
    headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
    r=requests.get(url, headers=headers)
    if r.status_code==200:
        # print('Status code', r.status_code)
        logging.info(f"✅ 連線成功。")
        soup=BeautifulSoup(r.content, parser="html.parser")
        posts=soup.find_all('h2')
    else:
        posts=[]
        logging.error(f"❌ {today} 連線失敗: {r.status_code}")
    return posts


logging.info(f"🚀 爬取《Jornal Tribunal de Macau》程式啟動。目前設定日期: {today}。")
posts=[]
for page in range(1,10):
    post=get_jtm_post_list(page)
    print(f'爬緊第{page}頁, 有{len(post)}條新聞')
    if post:
        posts+=post
    else:
        break
        
total_no_post=len(posts)
logging.info(f"成功獲取 {today} 數據，當日有{total_no_post}條新聞。")
print(f'JTM {today} 有{len(posts)}條新聞')

# %%
def get_article(url):
    headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
    r=requests.get(url, headers=headers)
    soup=BeautifulSoup(r.content, "html.parser")
    if soup.find('span', {'class': 'meta-date'}):
        # date=soup.find('span', {'class': 'meta-date'}).text
        # date=datetime.strptime(date, '%d %b, %Y').strftime('%Y-%m-%d %H:%M:%S')
        date_str=soup.find('span', {'class': 'meta-date'}).text
        dt = datetime.strptime(date_str, '%d %b, %Y')
        date = formatdate(time.mktime(dt.timetuple()))
    else:
        date = formatdate() # 萬一冇日期就用而家

    img_url = ""
    img_tag = soup.find('div', {'class': 'post-image-item'})
    if img_tag:
        img_url = img_tag.img.get('src')
    
    if soup.find('span', {'class': 'meta-author'}):
        author=soup.find('span', {'class': 'meta-author'}).text
        author=author if author!='' else 'None'
    else:
        author="None"
    
    if soup.find('h2', {'class': 'single-title'}):
        title=soup.find('h2', {'class': 'single-title'}).text
    else:
        title=None
    
    if soup.find('div', {'class': 'post-content entry clearfix'}):
        # content=soup.find('div', {'class': 'post-content entry clearfix'}).text.strip()
        content=soup.find('div', {'class': 'post-content entry clearfix'}).decode_contents()

        if img_url:
                content = f'<img src="{img_url}" style="width:100%; margin-bottom:10px;""")/>><br/>' + content
    else:
        content=None
    return date, title, author, content

# %%

if posts:
    restructured_posts=[]
    for idx, post in enumerate(posts):
        logging.info(f"正在爬取{idx+1}/{total_no_post}則新聞。")
        link=post.a.get('href')
        date, title, author, content=get_article(link)
        dict_post={
            'title': title,
            'author': author,
            'link': link,
            'date': date,
            'content': content
        }
        restructured_posts.append(dict_post)
        logging.info(f"✅ 成功獲取: {title}。")
        time.sleep(1.5) # 每次入內文前停一停，對人哋 Server 禮貌啲

    # %%

    import xml.etree.ElementTree as ET

    # Create the root of the RSS feed
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    # Add channel elements
    ET.SubElement(channel, 'title').text = 'Jornal TRIBUNA DE MACAU'
    ET.SubElement(channel, 'link').text = 'https://jtm.com.mo/'
    ET.SubElement(channel, 'description').text = 'Jornal TRIBUNA DE MACAU RSS'

    # Add items
    for item in restructured_posts:
        item_elem = ET.SubElement(channel, 'item')
        ET.SubElement(item_elem, 'title').text = item['title']
        ET.SubElement(item_elem, 'link').text = item['link']
        ET.SubElement(item_elem, 'description').text = item['content']
        ET.SubElement(item_elem, 'pubDate').text = item['date']

    # Convert to string and save to an XML file
    rss_feed = ET.tostring(rss, encoding='utf-8', method='xml').decode()
    xml_file_name='Jornal_TRIBUNA_DE_MACAU.xml'
    with open(xml_file_name, 'w', encoding='utf-8') as xml_file:
        xml_file.write(rss_feed)
    
    logging.info(f"✅ 成功保存: {xml_file_name}。")
else:
    logging.warning(f"⚠️ 當日沒有新聞。")
