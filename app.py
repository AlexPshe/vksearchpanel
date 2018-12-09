#Login/pass for VK API
login = 'vk.login'
password = 'vk.password'

from flask import Flask
from flask import render_template
from flask import request
import vk_api
from polyglot.text import Text
import re
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['elasticsearch'], port = 9200)
es = Elasticsearch(hosts=['elasticsearch'], port = 9200)

post_index = Index('post_index', using=es)
post_index.delete(ignore=404)
post_index.create()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search/q')
def search():
    query = request.args.get("search")
    sentiment = request.args.get("sentiment")

    db_history_search = es.search(index='post_index', doc_type='post',
                                  q=query)

    items = list()
    for post in db_history_search['hits']['hits']:
        if sentiment == "positive" and post['_source']['score'] > 0.1:
            items.append(
                [post['_source']['message'], post['_source']['score'],
                 post['_source']['views'], post['_source']['likes'],
                 post['_source']['date']])
        elif sentiment == "negative" and post['_source']['score'] < -0.1:
            items.append(
                [post['_source']['message'], post['_source']['score'],
                 post['_source']['views'], post['_source']['likes'],
                 post['_source']['date']])
        elif sentiment == "neutral" and post['_source'][
            'score'] > -0.1 and post['_source']['score'] < 0.1:
            items.append(
                [post['_source']['message'], post['_source']['score'],
                 post['_source']['views'], post['_source']['likes'],
                 post['_source']['date']])

    if len(items) == 0:
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
                post_date = datetime.utcfromtimestamp(
                    int(post['date'])).strftime('%Y-%m-%d')
                posts_clean.append(
                    [post['text'], post['views']['count'],
                     post['likes']['count'], post_date])

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
                items.append(
                    [post[0], polarity, post[1], post[2], post[3]])
            elif polarity < -0.1 and sentiment == "negative":
                items.append(
                    [post[0], polarity, post[1], post[2], post[3]])
            elif polarity > -0.1 and polarity < 0.1 and sentiment == "neutral":
                items.append(
                    [post[0], polarity, post[1], post[2], post[3]])
            es.index(index='post_index', doc_type="post",
                     body={'message': post[0], 'score': polarity,
                           'views': post[1], 'likes': post[2],
                           'date': post[3]})

    #message score tags author date
    return render_template('search.html', items = items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
