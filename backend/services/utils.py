from services.models import Service
import mysql.connector
import MySQLdb
import sys
import json
from pysolr import Solr
import environ

# Environment variables
env = environ.Env()
environ.Env.read_env()

def get_db_instance():
    return MySQLdb.Connect(
        host = "localhost",
        port = 3306,
        user = env('SILVERCARE_DATABASE_USER'),
        passwd = env('SILVERCARE_DATABASE_PASSWORD'),
        db = env('SILVERCARE_DATABASE_NAME')
    )

def delete_service_solr(id):
    conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
    id_str = str(id)
    conn.delete(q=f'id:{id_str}')
    conn.commit()

def add_service_solr(name,organiser):
    conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
    results = conn.search('*:*', rows=0)
    id = 1 + results.hits
    var = {'id':str(id),
            'name':str(name),
            'organiser':str(organiser)}
    conn.add([var])
    conn.commit()

def add_everything_solr():
    conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
    mycursor = get_db_instance().cursor()
    mycursor.execute("SELECT * FROM services_service")
    for field in mycursor.fetchall():
        var = {'id':str(field[0]),
                'name':str(field[4]),
                'organiser':str(field[7])}
        conn.add([var])
        conn.commit()

def print_everything_from_solr():
    conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
    results = conn.search('*:*') 
    for result in results:
        print(result)