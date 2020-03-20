import requests
from bs4 import BeautifulSoup
import time
import pickle
import sys
sys.setrecursionlimit(10000)


website_url = "https://lacrima.jp/"
category_urls = list()
scraped_urls = set()
happy_episodes = list()

r = requests.get(website_url)

soup1 = BeautifulSoup(r.content, "html.parser")

categorys = soup1.find_all("li", attrs={"class", "cat-item"})

# get category urls
for category in categorys:
    category_url = category.find("a").get("href")
    category_urls.append(category_url)

# request each category urls
for category_url in category_urls:
    page_index = 1
    while True:
        time.sleep(2)
        request_url = category_url + "page/" + str(page_index) + "/"
        # https://lacrima.jp/category/pet/page/6/などにアクセス
        r = requests.get(request_url)
        # 存在するページならば
        if r.status_code == 200:
            page_index += 1
            scraping_urls = BeautifulSoup(r.content, "html.parser").find_all("a", attrs={"class", "more-link"})
            for scraping_url in scraping_urls:
                # scraped_urlは実際にスクレピングする対象
                scraped_url = scraping_url.get("href")

                # すでにスクレイピング済みならば無視
                if scraped_url in scraped_urls:
                    continue
                # スクレイピング開始
                time.sleep(2)
                r = requests.get(scraped_url)
                # スクレイピング済みの辞書に追加
                scraped_urls.add(scraped_url)
                # タイトルと本文を検索
                article = BeautifulSoup(r.content, "html.parser").find("article")
                # タイトル習得
                main_title = article.find("h1", attrs={"class", "entry-title"}).text
                # 画像url習得
                image_url = article.find("img")["src"]
                # カテゴリ習得
                category_tags = article.find("div", attrs={"class", "blogbox"}).find_all("a")
                tmp = []
                for c_tag in category_tags:
                    tmp.append(c_tag.text)
                category_tag = " ".join(tmp)
                # 本文習得
                main_contents = article.find_all("p")
                tmp = []
                for p_tag in main_contents:
                    tmp.append(p_tag.text)
                content = "\n".join(tmp)
                # 追加するエピソード詳細
                append_dict = {
                    "title": main_title,
                    "category": category_tag,
                    "image_url": image_url,
                    "content": content
                }
                happy_episodes.append(append_dict)

                print(main_title, image_url, type(append_dict['title']), type(append_dict['content']))
        # 存在しないページだから次のカテゴリーへ
        else:
            # print("status is bad => break")
            break

# pickle化
f = open('./data/happy_episodes_add_image_url_list.bin', 'wb')
pickle.dump(happy_episodes, f)
f.close()