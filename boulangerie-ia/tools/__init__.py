from .notion_tools import consulter_stocks, consulter_catalogue, consulter_ventes

from .email_tool import envoyer_commande_fournisseur
from .forecast_tool import prevoir_production

ALL_TOOLS = [
    consulter_stocks,
    consulter_catalogue,
    consulter_ventes,
    envoyer_commande_fournisseur,
    prevoir_production,
]
