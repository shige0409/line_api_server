from flask import Flask, request, abort

import os
import pickle
import random

from datetime import datetime, timedelta, timezone

from main import app, db
from main.models import Entry

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, FlexSendMessage
)

# 感動エピソード読み込み
f = open('./data/happy_episodes_add_image_url_list.bin', 'rb')
happy_episodes = pickle.load(f)
f.close()



#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN_TEST"]
YOUR_CHANNEL_SECRET = os.environ["YOU_CHANNEL_SECRET_TEST"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # user_id
    u_id = event.source.user_id
    # 読んだ日付
    JST = timezone(timedelta(hours=+9), 'JST')
    dt_now = datetime.now(JST)
    insert_date = "{}/{}/{}".format(dt_now.year, dt_now.month, dt_now.day)
    # テキスト
    text = event.message.text
    print(text)

    # 今日の閲覧回数が3回を超えたら見せないようにする
    if Entry.query.filter(Entry.user_id == u_id, Entry.read_date == insert_date).count() >= 3:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="３回見てるから今日はごめんね\uDBC0\uDC17\nまた明日見てね\uDBC0\uDC08"))
    elif text == "感動":
        # insert db
        try:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="よかった\uDBC0\uDC05次も楽しみにしててね\uDBC0\uDC02"))
            fixing_entry = db.session.query(Entry).filter_by(user_id = u_id).order_by(Entry.id.desc()).first()
            fixing_entry.is_good = text
            db.session.add(fixing_entry)
            db.session.commit()
        except:
            pass
    elif text == "普通":
        # insert db
        try:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="ごめんね\uDBC0\uDC17調整するね\uDBC0\uDC10"))
            fixing_entry = db.session.query(Entry).filter_by(user_id = u_id).order_by(Entry.id.desc()).first()
            fixing_entry.is_good = text
            db.session.add(fixing_entry)
            db.session.commit()
        except:
            pass
    else:
        happy_episode = random.choice(happy_episodes)
        content = ""
        if happy_episode['content'].split("\n")[1] == "":
            content = "\n".join(happy_episode['content'].split("\n")[2:])
        else:
            content = "\n".join(happy_episode['content'].split("\n")[1:])
        payload = {
            "type": "flex",
            "altText": "Flex Message",
            "contents": {
                "type": "bubble",
                "hero": {
                "type": "image",
                "url": happy_episode['image_url'],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "label": "lacrima",
                    "uri": "https://lacrima.jp/"
                }
                },
                "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                    "type": "text",
                    "text": happy_episode['title'],
                    "size": "xl",
                    "weight": "bold"
                    },
                    {
                    "type": "text",
                    "text": content,
                    "wrap": True
                    }
                ]
                },
                "footer": {
                "type": "box",
                "layout": "horizontal",
                "flex": 0,
                "spacing": "sm",
                "contents": [
                    {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "(-_-)",
                        "text": "普通"
                    },
                    "height": "sm"
                    },
                    {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "(^o^)",
                        "text": "感動"
                    },
                    "height": "sm"
                    }
                ]
                }
            }
        }
        
        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage.new_from_json_dict(payload)
        )
        # データベースに挿入
        try:
            entry = Entry(
                user_id = u_id,
                send_message = text,
                read_title = happy_episode["title"],
                read_image_url = happy_episode["image_url"],
                is_good = "",
                read_date = insert_date
            )
            db.session.add(entry)
            db.session.commit()
        except:
            print("db insert error")


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)