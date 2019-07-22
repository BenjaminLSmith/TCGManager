from tcgmanager.helpers.esconnection import ESConnectionBase
from tcgmanager.helpers.tcgplayer import TCGPlayerBase

import logging

LOG = logging.getLogger(name=__name__)


class UpdateDocsBase:
    def __init__(self, esHost):
        self.es = ESConnectionBase(esHost)
        self.tcgapi = TCGPlayerBase()

    def getLatestPrices(self):
        # Get documents in Inventory
        res = self.es.getInvList()
        while len(res["hits"]["hits"]) > 0:
            results = res["hits"]["hits"]

            hitDictionary = {}
            productIDs = []
            for hit in results:
                docIDSplit = hit["_id"].split("-")
                hitDictionary[hit["_id"]] = hit["_source"]["cardName"]
                productIDs.append(docIDSplit[0])

            # Get prices for all productIDs in inventory
            prices = self.tcgapi.getMarketPricesByProductId(productIDs)
            if not prices["success"]:
                LOG.error(
                    "Failed to get pricing information during update: {}".format(
                        prices["errors"]
                    )
                )
                raise

            for priceObj in prices["results"]:
                priceId = "{}-{}".format(priceObj["productId"], priceObj["subTypeName"])
                if priceId in hitDictionary:
                    priceObj["cardName"] = hitDictionary[priceId]
                    # Insert priceObj into priceIndex
                    result = self.es.insertPriceDocument(priceObj)
                    LOG.debug(result)

            # Get next set of results
            res = self.es.getInvList(scrollId=res["_scroll_id"])

    def insertCard(self, productId, subType, listed, numCards):
        # Check if card exists already
        existingDoc = self.es.getCardByDocID("{}-{}".format(productId, subType))

        # Create document
        doc = {}
        if existingDoc:
            doc = existingDoc
            doc["numCards"] += numCards
        else:
            doc["productId"] = int(productId)
            doc["subTypeName"] = subType
            doc["isListed"] = listed
            doc["numCards"] = numCards

            # Get details for card
            ids = [productId]
            detailedResults = self.tcgapi.mtgCardDetails(ids)
            if not detailedResults["success"]:
                LOG.info("Failed to get card details. Exiting.")
                return

            doc["cardName"] = detailedResults["results"][0]["name"]
            doc["urlInfo"] = detailedResults["results"][0]["url"]

            for detail in detailedResults["results"][0]["extendedData"]:
                doc[detail["name"]] = detail["value"]

        # Insert document into ES
        result = self.es.insertInvDocument(doc)
        LOG.debug(result)
