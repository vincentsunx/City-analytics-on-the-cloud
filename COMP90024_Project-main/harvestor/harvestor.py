import tweepy
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
import os
from pprint import pprint
import couchdb
import json

def createdb(couchserver,dbname):
    if dbname in couchserver:
        return couchserver[dbname]
    else:
        return couchserver.create(dbname)

def create_region(couch_database):
    with open('region.json') as file:
        for region in file.readlines():
            data=json.loads(region)
            try:
                pushdata(data, 'region', couch_database)
            except:
                pass

def pushdata(data, database_name, couch_database):
    for db in couch_database:
        if db._name == database_name:
            db.save(data)
            break
    else:
        print('no such database')

f=open("ip.txt", "r")
couchdb_master_ip=f.readline().rstrip()
couchdb_master_login_url='http://admin:admin@'+couchdb_master_ip+':5984/'
db_children=f.read().splitlines()
f.close()

couchserver = couchdb.Server('http://'+couchdb_master_ip+':5984/')
couchserver.resource.credentials=('admin','admin')

couch_database = []
database_name = ['new_tweet','region']

for dbname in database_name:
    couch_database = couch_database+[createdb(couchserver,dbname)]
    for child in db_children:
        couchserver.replicate(couchdb_master_login_url+dbname,'http://admin:admin@'+child+':5984/'+dbname,create_target=True,continuous=True)

create_region(couch_database)

"""
for dbname in dbnamelist:
    self.db=self.db+[self.createdb(couchserver,dbname)]
    for child in db_children:
        couchserver.replicate(couchdb_master_login_url+dbname,'http://admin:admin@'+child+':5984/'+dbname,create_target=True,continuous=True)
"""



access_token = "1385967814641549321-gcI3aTWLxSoeIQZCxqvXnn6OzPkKhc"
access_token_secret = "V15cvOg2BrvdCxnMpaWzzucHnUuSbLCb4Le8u0qBpT6Ej"
consumer_key = "6YDJHTL8hQwX4CvmrWO9Y5190"
consumer_secret = "tIniChCVJZHOQU0jR0sSn3GFBZnG2p9kDX63nDCAubeZaeMpVs"
# bbox = {
#         "great_syd": [149.971885992, -34.33117400499998, 151.63054702400007, -32.99606922499993],
#         "great_mel": [144.33363404800002, -38.50298801599996, 145.8784120140001, -37.17509899299995],
#         "great_brisbane": [152.07339276400012, -28.363962911999977, 153.54670756200005, -26.452339004999942],
#         "great_ald": [138.435645001, -35.350296029999974, 139.04403010400003, -34.50022530299998]
        #   "great_can": [148.764094, -35.916599, 149.393887,-35.125151]
#     }
# bounding = [113.338953078, -43.6345972634, 153.569469029, -10.6681857235]
bounding = [149.971885992, -34.33117400499998, 151.63054702400007, -32.99606922499993,144.33363404800002, -38.50298801599996, 145.8784120140001, -37.17509899299995,152.07339276400012, -28.363962911999977, 153.54670756200005, -26.452339004999942,138.435645001, -35.350296029999974, 139.04403010400003, -34.50022530299998,148.764094, -35.916599, 149.393887,-35.125151,115.617614368,-32.675715325,116.239023008,31.6244855145]
n_tweets = 0
# Create the class that will handle the tweet stream
class StdOutListener(StreamListener):
      
    def on_data(self, data):   
        global n_tweets
        #print(n_tweets)
        #n_tweets+=1
        tweet = json.loads(data)
        # print(type(tweet))
        new_twt =({"id":str(tweet['id']), "text":str(tweet['text']), "created_at":str(tweet['created_at']), "hastags":str(tweet['entities']['hashtags']), "user_mentions":(tweet['entities']['user_mentions']), "city":str(tweet['place']['name']), "box":str(tweet['place']['bounding_box']['coordinates'])})
        pushdata(new_twt,'new_tweet',couch_database)
        #print(new_twt)
        # new_twt =''
        return True
        

    def on_error(self, status):
        print(status)


if __name__ == '__main__':  
# Handle Twitter authetification and the connection to Twitter Streaming API
    
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(languages=["en"],locations=bounding)


print('------------------')
