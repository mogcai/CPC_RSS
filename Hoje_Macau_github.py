# %%
import logging
import re
import time
from datetime import datetime
from email.utils import formatdate  # 用嚟整標準 RSS 時間格式

import requests
from bs4 import BeautifulSoup

# 基本設定
logging.basicConfig(
    level=logging.INFO,  # 設定顯示邊個等級以上嘅訊息
    format="%(asctime)s - %(levelname)s - %(message)s",  # 設定格式：時間 - 等級 - 內容
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("news.log", encoding="utf-8"),  # 儲存到檔案
        logging.StreamHandler(),  # 同時噴喺 Console
    ],
)
# %%

today = (datetime.today()).strftime("%Y/%m/%d")
logging.info(f"🚀 爬取《Hoje Macau》程式啟動。目前設定日期: {today}。")
url = f"https://hojemacau.com.mo/{today}/"
headers = {
    "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
}
r = requests.get(url, headers=headers)

# %%
if r.status_code == 200:
    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
    lst_post = soup.find_all("h2", {"class": re.compile("entry-title")})
    total_no_post = len(lst_post)
    logging.info(f"成功獲取 {today} 數據，當日有{total_no_post}條新聞。")
else:
    logging.error(f"❌ {today} 連線失敗: {r.status_code}")
    lst_post = []


# %%
def get_article(url):
    headers = {
        "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")

    if date_tag := soup.find("time", {"class": re.compile("entry-date")}):
        date_str = date_tag.get("datetime")
        dt = datetime.fromisoformat(date_str)
        date = formatdate(time.mktime(dt.timetuple()))
    else:
        date = formatdate()  # 萬一冇日期就用而家

    img_url = ""

    if img_tag := soup.find("div", {"class": re.compile("post-thumbnail")}):
        img_url = img_tag.img.get("src")

    if content_tag := soup.find("div", {"class": "entry-content"}):
        content = content_tag.decode_contents()

        if img_url:
            content = (
                f'<img src="{img_url}" style="width:100%; margin-bottom:10px;""")/>><br/>'
                + content
            )
    else:
        content = None

    if cat_tag := soup.find("a", {"rel": re.compile("category tag")}):
        cat = cat_tag.text.strip()
    else:
        cat = None

    if author_tag := soup.find("a", {"class": re.compile("author")}):
        author = author_tag.text.strip()
    else:
        author = None

    return date, content, cat, author


total_no_post = 0
if lst_post:
    restructured_posts = []
    for idx, post in enumerate(lst_post):
        logging.info(f"正在爬取{idx + 1}/{total_no_post}則新聞。")
        title = post.a.text
        link = post.a.get("href")
        date, content, cat, author = get_article(link)

        dict_post = {
            "title": title,
            "category": cat,
            "author": author,
            "link": link,
            "date": date,
            "content": content,
        }
        restructured_posts.append(dict_post)
        logging.info(f"✅ 成功獲取: {title}。")
        time.sleep(1.5)  # 每次入內文前停一停，對人哋 Server 禮貌啲

    # %%
    import xml.etree.ElementTree as ET

    # Create the root of the RSS feed
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # Add channel elements
    ET.SubElement(channel, "title").text = "Hoje Macau"
    ET.SubElement(channel, "link").text = url
    ET.SubElement(channel, "description").text = "Hoje Macau RSS"

    # Add items
    for item in restructured_posts:
        item_elem = ET.SubElement(channel, "item")
        ET.SubElement(item_elem, "title").text = item["title"]
        ET.SubElement(item_elem, "link").text = item["link"]

        # If using BeautifulSoup, it's safer to use .decode_contents() for HTML
        # or .get_text() for plain text.
        content = item["content"]
        ET.SubElement(item_elem, "description").text = content

        ET.SubElement(item_elem, "pubDate").text = item["date"]

    # Convert to string and save to an XML file
    rss_feed = ET.tostring(rss, encoding="utf-8", method="xml").decode()
    xml_file_name = "Hoje_Macau.xml"
    with open(xml_file_name, "w", encoding="utf-8") as xml_file:
        xml_file.write(rss_feed)
    logging.info(f"✅ 成功保存: {xml_file_name}。")
else:
    logging.warning("⚠️ 沒有新聞。")
