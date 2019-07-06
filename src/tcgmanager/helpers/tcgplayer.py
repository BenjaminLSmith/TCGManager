import json
import logging
import requests

from datetime import datetime
from os import path
from urllib.parse import urlencode

LOG = logging.getLogger(name=__name__)


class TCGPlayerBase:
    def __init__(self):
        self.authCode = self.getAuthCode()
        self.host = "http://api.tcgplayer.com/v1.27.0"

    # Determines if current auth code is valid. If not, generate a new one
    def getAuthCode(self):
        # Check if current auth code exists
        if path.exists("secrets/authcode"):
            with open("secrets/authcode", "r") as f:
                authcodeRaw = f.readline()
            authcodeJSON = json.loads(authcodeRaw)

            # Check if auth code is still valid
            now = datetime.now()
            expires = datetime.strptime(
                authcodeJSON[".expires"], "%a, %d %b %Y %H:%M:%S GMT"
            )
            if now > expires:
                return self.authenticate()
            else:
                return authcodeJSON["access_token"]
        else:
            return self.authenticate()

    # Returns a new authentication code
    def authenticate(self):
        with open("secrets/key.pub", "r") as f:
            public_key = f.readline()

        with open("secrets/key.priv", "r") as f:
            private_key = f.readline()
        url = "https://api.tcgplayer.com/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = "grant_type=client_credentials&client_id={}&client_secret={}".format(
            public_key.strip(), private_key.strip()
        )
        r = requests.post(url, data=body, headers=headers)
        # Write new auth code to file & return code
        resp = json.loads(r.text)
        with open("secrets/authcode", "w+") as f:
            f.write(r.text)

        return resp["access_token"]

    # Returns a JSON array of the categories available
    def listCategories(self):
        endpoint = "/catalog/categories"
        url = self.host + endpoint

        headers = {"Authorization": "bearer {}".format(self.authCode)}

        results = json.loads(requests.get(url, headers=headers).text)
        maxResults = results["totalItems"]
        currResults = results["results"]
        while len(currResults) < maxResults:
            newUrl = url + "?offset={}".format(len(currResults))
            pagResults = json.loads(requests.get(newUrl, headers=headers).text)
            currResults.extend(pagResults["results"])

        return currResults

    # Returns a results response searching by card name
    def mtgCardSearch(self, name=None):
        endpoint = "/catalog/products"
        headers = {"Authorization": "bearer {}".format(self.authCode)}
        params = {"categoryId": 1, "productTypes": "Cards"}

        params["productName"] = name

        url = "{}{}".format(self.host, endpoint)

        results = json.loads(requests.get(url, headers=headers, params=params).text)
        return results

    # Gets card details with a list of product IDs
    def mtgCardDetails(self, productIds):
        params = {"includeSkus": False, "getExtendedFields": True}
        endpoint = "/catalog/products/{}".format(",".join(str(x) for x in productIds))
        url = "{}{}".format(self.host, endpoint)
        headers = {"Authorization": "bearer {}".format(self.authCode)}
        results = json.loads(requests.get(url, headers=headers, params=params).text)

        LOG.debug(json.dumps(results, indent=4, sort_keys=True))
        return results

    def getMarketPricesByProductId(self, productIds):
        endpoint = "/pricing/product/{}".format(",".join(str(x) for x in productIds))
        url = "{}{}".format(self.host, endpoint)
        headers = {"Authorization": "bearer {}".format(self.authCode)}

        results = json.loads(requests.get(url, headers=headers).text)

        LOG.debug(json.dumps(results, indent=4, sort_keys=True))
        return results
