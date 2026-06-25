# %%
# %%
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
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
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y/%m/%d")

target_dates = [today, yesterday]


logging.info(f"🚀 爬取《All In Media》程式啟動。目前設定日期: {today}。")
valid_post = []
for target_date_str in target_dates:
    url = f"https://www.allinmedia.com.hk/{target_date_str}/"
    headers = {
        "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    }
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")

        if content_tag := soup.find("div", class_="td-pb-span8 td-main-content"):
            posts = content_tag.find_all("h3", class_="entry-title td-module-title")
            valid_post += list(set([post.find("a").get("href") for post in posts]))
            total_no_post = len(valid_post)
            logging.info(
                f"✅ 成功獲取 {target_date_str} 數據，當日有{total_no_post}條新聞。"
            )
        else:
            logging.error(f"❌ {target_date_str} 沒有內容")
    else:
        logging.error(f"❌ {target_date_str} 連線失敗: {r.status_code}")


# %%
def get_article(url):
    headers = {
        "USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
            data = soup.find_all("div", {"class": "td-pb-span8"})[-1]
            date_tag = data.find("time", {"class": "entry-date"})
            if date_tag and date_tag.get("datetime"):
                try:
                    dt = datetime.fromisoformat(date_tag.get("datetime"))
                    # dt.timestamp() handles the +08:00 conversion to GMT correctly
                    date = formatdate(dt.timestamp(), usegmt=True)
                except ValueError:
                    date = formatdate()  # Fallback for weird formats
            else:
                date = formatdate()  # Use current time if missing

            if title_tag := soup.find("h1", {"class": re.compile("entry-title")}):
                title = title_tag.get_text().strip()
            else:
                title = "NA"

            if author_tag := data.find("a", {"class": re.compile("tdb-author-name")}):
                author = author_tag.get_text().strip()
            else:
                author = "NA"

            img_url = ""
            if img_tag := data.find(
                "div", {"class": re.compile("td-post-featured-image")}
            ):
                img_url = img_tag.img.get("src")

            if content_tag := data.find(
                "div", {"class": re.compile("td-post-content")}
            ):
                content = content_tag.get_text().strip()

                if img_url:
                    content = (
                        f'<img src="{img_url}" style="width:100%; margin-bottom:10px;""")/>><br/>'
                        + content
                    )
            else:
                content = "NA"

            if cat_tag := data.find("li", {"class": re.compile("entry-category")}):
                cat = cat_tag.get_text().strip()
            else:
                cat = "NA"
            return date, title, cat, author, content
        else:
            logging.error(f"❌ 文章連線失敗: {r.status_code}, {url}")
    except Exception as e:
        logging.error(f"❌ Error Scraping {url}: {e}")

    return "NA", "NA", "NA", "NA", "NA"


# %%
restructured_posts = []
total_no_post = len(valid_post)
for idx, url in enumerate(valid_post):
    logging.info(f"正在爬取{idx + 1}/{total_no_post}則新聞。")
    date, title, cat, author, content = get_article(url)
    dict_post = {
        "title": title,
        "category": cat,
        "author": author,
        "link": url,
        "date": date,
        "content": content,
    }
    restructured_posts.append(dict_post)
    logging.info(f"✅ 成功獲取: {title}。")

# %%


# Create the root of the RSS feed
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")

# Add channel elements
ET.SubElement(channel, "title").text = "Allinmedia"
ET.SubElement(channel, "link").text = r"https://www.allinmedia.com.hk/"
ET.SubElement(channel, "description").text = "Allinmedia RSS"

# Add items
for item in restructured_posts:
    item_elem = ET.SubElement(channel, "item")
    ET.SubElement(item_elem, "title").text = item["title"]
    ET.SubElement(item_elem, "link").text = item["link"]
    ET.SubElement(item_elem, "description").text = item["content"]
    ET.SubElement(item_elem, "pubDate").text = item["date"]

# Convert to string and save to an XML file
rss_feed = ET.tostring(rss, encoding="utf-8", method="xml").decode()
with open("Allinmedia.xml", "w", encoding="utf-8") as xml_file:
    xml_file.write(rss_feed)
