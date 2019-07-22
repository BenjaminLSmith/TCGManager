import click
import click_log
import logging
import os

from tcgmanager.helpers.tcgplayer import TCGPlayerBase
from tcgmanager.helpers.esconnection import ESConnectionBase
from tcgmanager.services.docupdates import UpdateDocsBase

# Basic Logging
LOG = logging.getLogger()
click_log.basic_config(logger=LOG)
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
"""path: path to install location of package
"""


class ContextCLI:
    def __init__(self):
        self.obj = {}
        self.cwd = os.getcwd()


PASS_CONTEXT = click.make_pass_decorator(ContextCLI, ensure=True)
CONTEXT_SETTINGS = dict(auto_envvar_prefix="TCG", help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click_log.simple_verbosity_option(LOG, default="WARNING", metavar="LEVEL")
@click.version_option()
@click.option(
    "--es-host",
    "esHost",
    prompt=False,
    default=lambda: os.environ.get("TCG_ES_HOST", ""),
    help="Elasticsearch host to interact with",
)
@PASS_CONTEXT
def cli(ctx, esHost: str):
    ctx.obj["ELASTIC_HOST"] = esHost


@cli.command("cardNameSearch")
@click.option(
    "--name",
    "mtgCardName",
    prompt="MTG card to get details for",
    help="MTG card to get details for",
)
@PASS_CONTEXT
def searchCardByName(ctx, mtgCardName: str):
    tcgapi = TCGPlayerBase()
    results = tcgapi.mtgCardSearch(mtgCardName)

    if not results:
        return
    elif len(results["results"]) < 1:
        print(results["errors"][0])
        return

    # Pretty output
    print("{} Results Found".format(results["totalItems"]))
    print("Sample of item information:")
    for result in results["results"]:
        print(
            "Product ID: {}, Name: {}, Url: {}".format(
                result["productId"], result["name"], result["url"]
            )
        )


@cli.command("insertCard")
@click.option(
    "--productId",
    "cardProductId",
    prompt="MTG Card Product ID",
    help="Product ID of the MTG card to add",
)
@click.option(
    "--subType",
    "cardSubType",
    prompt="What is the card subtype",
    type=click.Choice(["Normal", "Foil"]),
    help="Card Subtype to insert into datastore",
)
@click.option(
    "--listed/--not-listed",
    "isCardListed",
    prompt="Is the card currently listed on marketplace",
    help="Is card currently listed on TCGPlayer Marketplace",
    default=False,
)
@click.option(
    "--num-cards",
    "numberOfCard",
    prompt="How many of this card do you have",
    help="The count of cards of this type",
    default=1,
)
@PASS_CONTEXT
def insertCardIntoES(
    ctx, cardProductId: str, cardSubType: str, isCardListed: bool, numberOfCard: int
):
    docBase = UpdateDocsBase(ctx.obj["ELASTIC_HOST"])
    docBase.insertCard(cardProductId, cardSubType, isCardListed, numberOfCard)


@cli.command("getLatestPrices")
@PASS_CONTEXT
def getLatestPrices(ctx):
    # Setup
    docBase = UpdateDocsBase(ctx.obj["ELASTIC_HOST"])
    docBase.getLatestPrices()
