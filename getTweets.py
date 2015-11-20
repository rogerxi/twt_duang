import oauth2 as oauth
import urllib
import simplejson as json
import sqlite3 as lite
import os
import re
import time
import datetime

## define a function to create a sql statement to insert records into table nodes
def sql_insert_nodes(curs, id, label, datetime):
  curs.execute('SELECT COUNT(*) FROM nodes WHERE user_id = ' + str(id))
  node = curs.fetchall()
  if (node[0][0]== 0):
    ts = time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(datetime, '%a %b %d %H:%M:%S +0000 %Y'))
    insert_statement = 'INSERT INTO nodes VALUES (' + str(id) + ','
    insert_statement += '"' + label + '",'
    insert_statement += '"' + ts + '")'
    curs.execute(insert_statement)

## query
def query(q, lat, lng, r, tweets):
  url = """https://api.twitter.com/1.1/search/tweets.json?q=%s&include_entities=true&until=%s&geocode=%s,%s,%smi&count=%d""" \
            % (q,datetime.date.today(),lat,lng,r,tweets)

  ## stream data
  header, fhand = client.request(url, method="GET")
  jDoc = json.loads(fhand, encoding='utf8')

  ## build a sqlite database
  db_directory = '...'
  if not os.path.exists(db_directory):
    os.makedirs(db_directory)

  db_path = db_directory + 'duang.db'
  con = lite.connect(db_path)

  user_ids = dict()
  user_labels = dict()
  ## create tables and insert records
  with con:
    curs = con.cursor()
    ## create a table to store nodes (name, date/time)
    # curs.execute('DROP TABLE IF EXISTS nodes')
    curs.execute('CREATE TABLE IF NOT EXISTS nodes (user_id TEXT, user_label TEXT, created_at TIMESTAMP, PRIMARY KEY (user_id))')
    ## create a table to store link (source, target, date/time)
    # curs.execute('DROP TABLE IF EXISTS links')
    curs.execute('CREATE TABLE IF NOT EXISTS links (tweet_id INT, source TEXT, target TEXT, created_at TIMESTAMP, \
                                      PRIMARY KEY (tweet_id, source, target, created_at))')
    ## insert tables: nodes, links
    for tweet in jDoc['statuses']:
      ## search the screen name of target user
      search_obj = re.findall(r'@\w+', tweet['text'])
      ## unique target users
      search_obj = set(search_obj)
      ## if it is a reply message
      if (search_obj):
        ## the id of source user
        source_id = tweet['user']['id']
        source_label = tweet['user']['screen_name']
        ## match if the source user screen name is valid [a-zA-Z0-9_]
        if (re.match(r'^\w+$', source_label, re.M|re.I) == None):
          continue
        ## for each target user 
        for at_screen_name in search_obj:
          at_screen_name = at_screen_name[1:]
          if (at_screen_name not in user_labels):
            ## stream user data from Twitter API
            url = """https://api.twitter.com/1.1/users/show.json?screen_name=%s""" % at_screen_name
            header, fhand = client.request(url, method="GET")
            target_user = json.loads(fhand, encoding='utf8')
            ## check if the user exists
            if (target_user and at_screen_name == target_user['screen_name']):
              target_id = target_user['id']
              target_label = at_screen_name
              user_ids[target_id] = target_label
              user_labels[target_label] = target_id
              ## insert target user into table nodes
              insert_statement = sql_insert_nodes(curs, target_id, target_label, target_user['created_at'])
          if (at_screen_name in user_labels):            
            if (source_id not in user_ids):
              user_ids[source_id] = source_label
              user_labels[source_label] = source_id
              ## insert the source user into table nodes
              insert_statement = sql_insert_nodes(curs, source_id, source_label, tweet['user']['created_at'])
            ## insert table links
            curs.execute('SELECT COUNT(*) FROM links WHERE tweet_id = ' + str(tweet['id']))
            node = curs.fetchall()
            if (node[0][0]== 0):
              ts = time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))
              insert_statement = 'INSERT INTO links VALUES (' + str(tweet['id']) + ','
              insert_statement += str(source_id) + ','
              insert_statement += str(user_labels[at_screen_name]) + ','
              insert_statement += '"' + ts + '")'
              curs.execute(insert_statement)
    con.commit()

## set up an app Tweet_Duang in https://apps.twitter.com/
## set consumer / access tokens
consumer_key='cqgQXo17lhZnMGqu3zuKGeOTv'
consumer_secret='r4d0ck8rAsOkWd7Vn4NhQ8T6xV6Y0Y2rLEfLduNSEujLP8uorW'
access_token_key='2741532921-uHusYNzfhmlYeGUDeVkH1PD8hBmyDLqSvj36Ecb'
access_token_secret='Q7U8uk0z8uL1m1kd9CrVrFp662JZypTXeNiGv1Qax1FMO'
consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
token = oauth.Token(key=access_token_key, secret=access_token_secret)
client = oauth.Client(consumer, token)

## query
lat = '48.8567'     # Paris: latitude
lng = '2.3508'      # Paris: longitude 
r = "200"           # radius 
tweets = 1000
query("terror", lat, lng, r, tweets)
query("attack", lat, lng, r, tweets)
query("le_bataclan", lat, lng, r, tweets)
query("kill", lat, lng, r, tweets)
query("refugee", lat, lng, r, tweets)
