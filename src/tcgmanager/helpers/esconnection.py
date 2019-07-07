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

    def insertPriceDocument(self, document):
        document["timestamp"] = datetime.utcnow()

        # Insert document into ES
        res = self.conn.index(
            index=self.priceIndex, body=document, doc_type="prices"
        )
        return res

    def getInvList(self):
        # Request to search entire inventory
        res = self.conn.search(index=self.invIndex, body={"query": {"match_all": {}}}, _source=False)
        return res["hits"]

    def getCardByDocID(self, docID):
        try:
            res = self.conn.get(index=self.invIndex, doc_type='cards', id=docID)
            LOG.debug(res)
            if res["found"]:
                return res["_source"]
            else:
                return None
        except NotFoundError:
            return None
