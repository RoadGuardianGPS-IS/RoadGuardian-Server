from typing import List
from db.segnalazione_repository import get_segnalazione_by_status, get_segnalazione_by_category

class MappaSegnalazioneFacade:
    """
    Facade Pattern: Fornisce un'interfaccia semplificata al sottosistema 'Gestione Segnalazione'
    per l'uso specifico da parte del sottosistema 'Gestione Mappa'.
    
    Nasconde la complessità delle query al database o delle logiche interne delle segnalazioni.
    """

    def get_segnalazioni_attive_per_mappa(self) -> List[dict]:
        """
        Scopo: Recupera le segnalazioni attive pronte per essere visualizzate sulla mappa.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - List[dict]: Lista di dizionari rappresentanti le segnalazioni attive.

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        # Qui incapsuliamo la chiamata al repository.
        # Se domani la logica cambia (es. bisogna chiamare un'API esterna invece di Mongo),
        # cambiamo solo qui e non in MappaService.
        return get_segnalazione_by_status(True)

    def get_segnalazioni_per_categoria(self, categoria: str) -> List[dict]:
        """
        Scopo: Recupera le segnalazioni filtrate per categoria.

        Parametri:
        - categoria (str): La categoria di segnalazione da filtrare.

        Valore di ritorno:
        - List[dict]: Lista di dizionari rappresentanti le segnalazioni della categoria specificata.

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        return get_segnalazione_by_category(categoria)
