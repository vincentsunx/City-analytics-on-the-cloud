# Part of COMP90024 Project Team members are
# Ziyuan Xiao (940448)
# Pengyu Mu(890756)
# Dechao Sun (980546)
# Seehoi Chow(980301)
# Yuexin Li (959634)

import couchdb2
from flask import current_app, g
from flask.cli import with_appcontext
import requests

MASTER_NODE = 'http://admin:admin@172.26.128.217:5984/'
NODE_1 = 'http://admin:admin@172.26.134.5:5984/'
NODE_2 = 'http://admin:admin@172.26.128.80:5984/'


def get_db(db_name):
    server = couchdb2.Server(MASTER_NODE)
    try:
        print(server)
    except requests.exceptions.ConnectionError:
        print(f'try node 2')
        server = couchdb2.Server(NODE_1)
        try:
            print(server)
        except requests.exceptions.ConnectionError:
            print(f'try node 3')
            server = couchdb2.Server(NODE_2)

    if db_name not in g:
        g.db_name = server[db_name]
    return g.db_name


server = couchdb2.Server(MASTER_NODE)
