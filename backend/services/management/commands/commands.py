from django.core.management.base import BaseCommand, CommandError
from services.models import Service
import mysql.connector
import sys
import json
from pysolr import Solr

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="3.1415",
    database="credentials"
)


class Command(BaseCommand):
   
    def add_everything_solr(self):
       conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
       mycursor = db.cursor()
       mycursor.execute(f"DESCRIBE services_service")
       for field in mycursor.fetchall():
                var = {'id':str(field[0]),
                       'name':str(field[1]),
                       'organiser':str(field[2])}
                conn.add([var])
                conn.commit()

    def delete_service_solr(self,id):
        conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
        id_str = str(id)
        conn.delete(q=f'id:{id_str}')
        conn.commit()

    def add_service_solr(self,name,organiser):
        conn = Solr('http://localhost:8983/solr/new_core', always_commit = True)
        results = conn.search('*:*', rows=0)
        id = 1 + results.hits
        var = {'id':str(id),
                'name':str(name),
                'organiser':str(organiser)}
        conn.add([var])
        conn.commit()