from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import logging

LOG = logging.getLogger(name=__name__)


class ESConnectionBase:
    def __init__(self, esHost):
        self.conn = Elasticsearch([esHost])
        self.invIndex = "mtg-inventory"
        self.priceIndex = "mtg-prices"

    def insertInvDocument(self, document):
        # create Document ID
        docID = "{}-{}".format(
            document["productId"], document["subTypeName"]
        )

        # Insert document into ES
        res = self.conn.index(
            index=self.invIndex, body=document, id=docID, doc_type="cards"
        )
        return res

    def getInvList(self):

        res = self.conn.search(
        )

        return res

    def getCardByDocID(self, docID):
        try:
            res = self.conn.get(index=self.invIndex, doc_type='cards', id=docID)
        except NotFoundError:
            return None
        finally:
            return res["_source"]
