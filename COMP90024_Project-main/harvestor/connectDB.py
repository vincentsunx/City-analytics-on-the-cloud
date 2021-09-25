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
database_name = ['tweet','region']

for dbname in database_name:
    couch_database = couch_database+[createdb(couchserver,dbname)]
    for child in db_children:
        couchserver.replicate(couchdb_master_login_url+dbname,'http://admin:admin@'+child+':5984/'+dbname,create_target=True,continuous=True)

create_region(couch_database)
