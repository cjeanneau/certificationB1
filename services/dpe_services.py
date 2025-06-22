from datetime import date, timedelta
import requests
from schemas import success_response, error_response

class DPEServices:
    """
    Classe pour interagir avec l'API DPE (Diagnostic de Performance Énergétique).
    """

    base_url_dpe = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
   

    @staticmethod
    def retrieve_recent_dpe_by_cp(cp: str, nb_jour) -> list:
        """
        Récupère tous les DPE pour un cp donnée pour les x derniers jours .

        Args:
            cp (str): code postal au format nnnnn.
            nb_jour (int): Nombre de jours pour lesquels récupérer les DPE récents.

        Returns:
            list: Liste des DPE récupérés ou None en cas d'erreur.
        """
        # Vérification du format du code postal
        if not cp or len(cp) != 5 or not cp.isdigit():
            raise ValueError("Le code postal doit être une chaîne de 5 chiffres.")
        
        # Déterminationd e la date à partir de laquelle on récupère des données
        date_etablissement = (date.today() - timedelta(days=nb_jour)).strftime('%Y-%m-%d')

        #Définition des champs de réponse
            # On ne récupère que les champs nécessaires pour éviter de surcharger la réponse
            # On pourra utiliser le numéro de dpe pour récupérer les détails si nécessaire
            # On utilise le champ identifiant_ban pour récupérer les détails de l'adresse
        response_fields = [
        "numero_dpe",
        "date_etablissement_dpe",
        "adresse_ban",
        "type_batiment",
        "surface_habitable_logement",
        "etiquette_dpe",
        "etiquette_ges",
        "identifiant_ban"
        ]
        # Préparation des paramètres de la requête
        params = {
            'qs': f"code_postal_ban:{cp} AND date_etablissement_dpe:[{date_etablissement} TO *]",
            'size': 100,
            'page': 1,
            'select': f"{','.join(response_fields)}"
        }
        
        try:
            response = requests.get(DPEService.base_url_dpe, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result:
                return success_response(
                    data=result.get('results', []),
                    message=f"{result.get('total', 0)} DPE récupérés pour le code postal {cp} depuis le {date_etablissement}",
                    count=result.get('total', 0),
                )
            else:
                return error_response(
                    message=f"Aucun DPE trouvé pour le code postal {cp} depuis le {date_etablissement}",
                    data=None
                )
        except requests.RequestException as e:
            print(f"Erreur Request API DPE: {str(e)}")
            return None
            

    @staticmethod
    def retrieve_dpe_by_num_dpe(num_dpe: str) -> dict:
        """
        Récupère un DPE spécifique par son numéro de DPE.

        Args:
            num_dpe (str): Numéro de DPE à rechercher.

        Returns:
            dict: tout le DPE trouvé ou None si non trouvé.
        """
        # Vérification du format du numéro de DPE
        if not num_dpe or len(num_dpe)!=  13:
            raise ValueError("Le numéro de DPE doit être une chaîne de 13 caractères alphanumériques.")
        
        # Préparation des paramètres de la requête
        params = {
            'qs': f"numero_dpe:{num_dpe}",
            'size': 1,
            'page': 1
        }
        
        try:
            response = requests.get(DPEService.base_url_dpe, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            dpe = result.get('results', {})
            nb_dpe = result.get('total', 0)
            if nb_dpe > 0:
                return success_response(
                    data=dpe,
                    message=f"DPE {num_dpe} récupéré avec succès",
                    count=nb_dpe,
                )
            else:
                return error_response(
                    message=f"Aucun DPE trouvé pour le numéro {num_dpe}",
                    data=None
                )

        except requests.RequestException as e:
            print(f"Erreur Request API DPE: {str(e)}")
            return None