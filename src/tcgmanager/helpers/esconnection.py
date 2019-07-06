from datetime import datetime
from elasticsearch import Elasticsearch

import logging

LOG = logging.getLogger(name=__name__)

class ESConnectionBase:
    def __init__(self, esHost):
        self.conn = Elasticsearch([esHost])


    def insertDocument(self, document):
        LOG.info("hi")
        # Insert time into document
        document['timestamp'] = datetime.utcnow()
        print(datetime.now())

        # Insert document into ES
        res = self.conn.index(index="mtg-cards", body=document)
        return res
