from flask import Flask
from flask import render_template
from flask import request
import vk_api
from polyglot.text import Text
import re
from polyglot.downloader import downloader
from datetime import datetime

password = "vk.password"
login = "vk.login"

downloader.download("TASK:sentiment2", quiet=False)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search/q')
def search():
    query = request.args.get("search")
    sentiment = request.args.get("sentiment")

    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    vk = vk_session.get_api()
    groups = ["40316705", "15755094"]
    posts = list()
    for group in groups:
        news = vk.wall.search(owner_id=("-" + group), query=query,
                              count=100, v="5.92", owners_only=0)
        news = news['items']

        for article in news:
            if article['post_type'] == 'post':
                posts.append(article)

    posts_clean = list()
    for post in posts:
        if post['text'] != '':
            post_date = datetime.utcfromtimestamp(int(post['date'])).strftime('%Y-%m-%d')
            posts_clean.append([post['text'], post['views']['count'],
                                post['likes']['count'], post_date])

    items = list()
    for post in posts_clean:
        text = re.sub(r"http\S+", "", post[0])
        text = Text(text)
        # calculate polarity
        polarity = 0
        norm = 0
        for w in text.words:
            polarity += w.polarity
            if polarity == w.polarity:
                norm += 0.1
            else:
                norm += 1
        polarity /= norm
        polarity = round(polarity, 2)
        if polarity > 0.1 and sentiment == "positive":
            items.append([post[0], polarity, post[1], post[2], post[3]])
        elif polarity < -0.1 and sentiment == "negative":
            items.append([post[0], polarity, post[1], post[2], post[3]])
        elif polarity > -0.1 and polarity < 0.1 and sentiment == "neutral":
            items.append([post[0], polarity, post[1], post[2], post[3]])

    # message score tags author date
    return render_template('search.html', items=items)
