from typing import Optional
from bddpg import get_session_sync, BienImmobilier, TransactionDVF, DPE
from sqlmodel import select, desc
from sqlalchemy import text
from schemas import success_response, error_response
from bddn4j import commune_graph_service



class EvalServices:
   
    @staticmethod
    def eval_by_cp(
        cp: str, 
        type_bien: Optional[str] = None, 
        surface_min: Optional[float] = None,
        surface_max: Optional[float] = None,
        etiquette_dpe: Optional[str] = None) -> dict:
        
        """
        Évaluation avec distinction des codes INSEE et étiquettes DPE
        Args:
            cp (str): Code postal à analyser
            type_bien (Optional[str]): Type de bien à filtrer (Maison, Appartement)
            surface_min (Optional[float]): Surface minimale à filtrer
            surface_max (Optional[float]): Surface maximale à filtrer
            etiquette_dpe (Optional[str]): Étiquette DPE à filtrer (A, B, C, D, E, F, G)
            Returns:
            dict: Statistiques détaillées par code_insee, type de bien et étiquette DPE
        """
        
        # On s'aasure que le code postal est valide
        if not cp or len(cp) != 5 or not cp.isdigit():
            return error_response(
                message="Le code postal doit être une chaîne de 5 chiffres.",
                error_code="INVALID_CP"
            )
        
        try:
            with get_session_sync() as session:
                
                # Entete de la requête SQL
                begin_sql = """
                SELECT 
                    c.code_postal,
                    c.code_insee_commune,
                    c.nom_commune,
                    bi.type_bien,
                    dpe.etiquette_dpe,
                    COUNT(*) as nb_transactions,
                    ROUND(AVG(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_moyen,
                    ROUND(MIN(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_min,
                    ROUND(MAX(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_max
                FROM transaction_dvf t
                JOIN bien_immobilier bi ON t.id_bien = bi.id_bien
                JOIN commune c ON bi.id_commune = c.id_commune
                JOIN dpe ON bi.id_bien = dpe.id_bien
                WHERE c.code_postal = :cp
                AND bi.surface_reelle_bati > 0
                AND t.valeur_fonciere > 0
                AND bi.type_bien IN ('Maison', 'Appartement')
                """

                # On ajouute des conditions dynamiquement si nécessaire
                # On utilise des paramètres pour éviter les injections SQL
                conditions = []
                params = {"cp": cp}
                
                if type_bien:
                    conditions.append("AND bi.type_bien = :type_bien")
                    params["type_bien"] = type_bien
                
                if surface_min:
                    conditions.append("AND bi.surface_reelle_bati >= :surface_min")
                    params["surface_min"] = surface_min
                    
                if surface_max:
                    conditions.append("AND bi.surface_reelle_bati <= :surface_max")
                    params["surface_max"] = surface_max
                    
                if etiquette_dpe:
                    conditions.append("AND dpe.etiquette_dpe = :etiquette_dpe")
                    params["etiquette_dpe"] = etiquette_dpe

                # On définit la fin de la requête SQL
                end_sql = """
                GROUP BY c.code_postal, c.code_insee_commune, c.nom_commune, bi.type_bien, dpe.etiquette_dpe
                ORDER BY c.code_insee_commune, bi.type_bien, dpe.etiquette_dpe, prix_m2_moyen DESC;
                """
                
                # Onconstruit la raquête SQL finale
                final_sql = begin_sql + " ".join(conditions) + end_sql
                
                # Debug
                #print("Reaquête SQLSQL:", final_sql)
                #print("Params:", params)
                
                results = session.connection().execute(text(final_sql), params).fetchall()
                
                if not results:
                    return error_response(
                        message=f"Aucune transaction trouvée pour le code postal {cp}",
                        error_code="NO_DATA_FOUND"
                    )

                # On va grouper par Communes (code_insee) → Types de bien → Étiquettes DPE
                communes = {}
                total_transactions = 0
                prix_global = []
                
                for row in results:
                    code_insee = row.code_insee_commune
                    type_bien_row = row.type_bien
                    etiquette_dpe = row.etiquette_dpe or "Non renseigné"
                    
                    # 1. On crée la commune si elle n'existe pas
                    if code_insee not in communes:
                        communes[code_insee] = {
                            "code_insee_commune": code_insee,
                            "nom_commune": row.nom_commune,
                            "types_biens": {},
                            "total_transactions_commune": 0,
                            "prix_m2_moyen_commune": 0
                        }
                    
                    # 2. On crée le type de bien si il n'existe pas
                    if type_bien_row not in communes[code_insee]["types_biens"]:
                        communes[code_insee]["types_biens"][type_bien_row] = {
                            "total_transactions_type": 0,
                            "prix_m2_moyen_type": 0,
                            "etiquettes_dpe": {}
                        }
                    
                    # 3. On ajoute les stats par étiquette DPE
                    communes[code_insee]["types_biens"][type_bien_row]["etiquettes_dpe"][etiquette_dpe] = {
                        "nb_transactions": int(row.nb_transactions),
                        "prix_m2_moyen": float(row.prix_m2_moyen) if row.prix_m2_moyen else 0.0,
                        "prix_m2_min": float(row.prix_m2_min) if row.prix_m2_min else 0.0,
                        "prix_m2_max": float(row.prix_m2_max) if row.prix_m2_max else 0.0
                    }
                    
                    # 4. On calcule le nb de transactions par type de bien
                    communes[code_insee]["types_biens"][type_bien_row]["total_transactions_type"] += int(row.nb_transactions)
                    
                    # 5. On calcule le nb de transactions par commune
                    communes[code_insee]["total_transactions_commune"] += int(row.nb_transactions)
                    
                    # 6. puis sur l'ensemble
                    total_transactions += int(row.nb_transactions)
                    
                    if row.prix_m2_moyen:
                        prix_global.extend([float(row.prix_m2_moyen)] * int(row.nb_transactions))

                # 7. On Calcul du prix moyen par type de bien et par commune
                for code_insee, commune_data in communes.items():
                    commune_prix = []
                    
                    for type_bien_key, type_data in commune_data["types_biens"].items():
                        type_prix = []
                        
                        # Prix moyen par type de bien basé sur les étiquettes DPE
                        for etiquette, stats in type_data["etiquettes_dpe"].items():
                            if stats["prix_m2_moyen"] > 0:
                                # Pondération par nombre de transactions
                                type_prix.extend([stats["prix_m2_moyen"]] * stats["nb_transactions"])
                                commune_prix.extend([stats["prix_m2_moyen"]] * stats["nb_transactions"])
                        
                        # Prix moyen par type de bien
                        type_data["prix_m2_moyen_type"] = round(
                            sum(type_prix) / len(type_prix) if type_prix else 0, 2
                        )
                    
                    # Prix moyen par commune
                    commune_data["prix_m2_moyen_commune"] = round(
                        sum(commune_prix) / len(commune_prix) if commune_prix else 0, 2
                    )

                # 7. On calcule le prix global sur l'ensemble de stransactions recueillies
                prix_global_moyen = sum(prix_global) / len(prix_global) if prix_global else 0.0
                
                # On contruit le resultat final
                result = {
                    "code_postal": cp,
                    "total_transactions": total_transactions,
                    "prix_m2_global_moyen": round(prix_global_moyen, 2),
                    "nb_communes": len(communes),
                    "communes": communes,
                    "metadata": {
                        "filtres_appliques": {
                            "type_bien": type_bien,
                            "surface_min": surface_min,
                            "surface_max": surface_max,
                            "etiquette_dpe": etiquette_dpe
                        }
                    }
                }
                
                return success_response(
                    data=result,
                    message=f"Évaluation du CP {cp} réussie avec {total_transactions} transactions dans {len(communes)} communes.",
                    count=total_transactions,
                )
                
        except Exception as e:
            return error_response(
                message=f"Erreur lors de l'analyse du CP {cp}: {str(e)}",
                error_code="DATABASE_ERROR",
                details={
                    "code_postal": cp,
                    "type_bien": type_bien,
                    "surface_min": surface_min,
                    "surface_max": surface_max,
                    "etiquette_dpe": etiquette_dpe,
                    "error_message": etiquette_dpe,
                    "error_type": type(e).__name__
                }
            )
        

    @staticmethod
    def eval_by_insee(
        code_insee: str, 
        type_bien: Optional[str] = None, 
        surface_min: Optional[float] = None,
        surface_max: Optional[float] = None,
        etiquette_dpe: Optional[str] = None) -> dict:
        
        """
        Évaluation avec distinction des codes postaux et étiquettes DPE
        Args:
            code_insee (str): Code insee à analyser
            type_bien (Optional[str]): Type de bien à filtrer (Maison, Appartement)
            surface_min (Optional[float]): Surface minimale à filtrer
            surface_max (Optional[float]): Surface maximale à filtrer
            etiquette_dpe (Optional[str]): Étiquette DPE à filtrer (A, B, C, D, E, F, G)
            Returns:
            dict: Statistiques détaillées par code_insee, type de bien et étiquette DPE
        """
        # On s'aasure que le code postal est valide
        if not code_insee or len(code_insee) != 5 or not code_insee.isdigit():
            return error_response(
                message="Le code postal doit être une chaîne de 5 chiffres.",
                error_code="INVALID_INSEE"
            )
        
        try:
            with get_session_sync() as session:
                
                # Entete de la requête SQL
                begin_sql = """
                SELECT 
                    c.code_postal,
                    c.code_insee_commune,
                    c.nom_commune,
                    bi.type_bien,
                    dpe.etiquette_dpe,
                    COUNT(*) as nb_transactions,
                    ROUND(AVG(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_moyen,
                    ROUND(MIN(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_min,
                    ROUND(MAX(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_max
                FROM transaction_dvf t
                JOIN bien_immobilier bi ON t.id_bien = bi.id_bien
                JOIN commune c ON bi.id_commune = c.id_commune
                JOIN dpe ON bi.id_bien = dpe.id_bien
                WHERE c.code_insee_commune = :code_insee
                AND bi.surface_reelle_bati > 0
                AND t.valeur_fonciere > 0
                AND bi.type_bien IN ('Maison', 'Appartement')
                """

                # On ajouute des conditions dynamiquement si nécessaire
                # On utilise des paramètres pour éviter les injections SQL
                conditions = []
                params = {"code_insee": code_insee}
                
                if type_bien:
                    conditions.append("AND bi.type_bien = :type_bien")
                    params["type_bien"] = type_bien
                
                if surface_min:
                    conditions.append("AND bi.surface_reelle_bati >= :surface_min")
                    params["surface_min"] = surface_min
                    
                if surface_max:
                    conditions.append("AND bi.surface_reelle_bati <= :surface_max")
                    params["surface_max"] = surface_max
                    
                if etiquette_dpe:
                    conditions.append("AND dpe.etiquette_dpe = :etiquette_dpe")
                    params["etiquette_dpe"] = etiquette_dpe

                # On définit la fin de la requête SQL
                end_sql = """
                GROUP BY c.code_insee_commune, c.code_postal, c.nom_commune, bi.type_bien, dpe.etiquette_dpe
                ORDER BY c.code_postal, bi.type_bien, dpe.etiquette_dpe, prix_m2_moyen DESC;
                """
                
                # Onconstruit la raquête SQL finale
                final_sql = begin_sql + " ".join(conditions) + end_sql
                
                # Debug
                print("Reaquête SQLSQL:", final_sql)
                print("Params:", params)
                
                results = session.connection().execute(text(final_sql), params).fetchall()
                print(results)
                if not results:
                    return error_response(
                        message=f"Aucune transaction trouvée pour le code insee {code_insee}",
                        error_code="NO_DATA_FOUND"
                    )

                # On va grouper par code_postal → Types de bien → Étiquettes DPE
                cp_communes = {}
                total_transactions = 0
                prix_global = []
                
                for row in results:
                    code_postal = row.code_postal
                    type_bien_row = row.type_bien
                    etiquette_dpe = row.etiquette_dpe or "Non renseigné"
                    
                    # 1. On crée la commune si elle n'existe pas
                    if code_postal not in cp_communes:
                        cp_communes[code_postal] = {
                            "code_postal_commune": code_postal,
                            "nom_commune": row.nom_commune,
                            "types_biens": {},
                            "total_transactions_commune": 0,
                            "prix_m2_moyen_commune": 0
                        }
                    
                    # 2. On crée le type de bien si il n'existe pas
                    if type_bien_row not in cp_communes[code_postal]["types_biens"]:
                        cp_communes[code_postal]["types_biens"][type_bien_row] = {
                            "total_transactions_type": 0,
                            "prix_m2_moyen_type": 0,
                            "etiquettes_dpe": {}
                        }
                    
                    # 3. On ajoute les stats par étiquette DPE
                    cp_communes[code_postal]["types_biens"][type_bien_row]["etiquettes_dpe"][etiquette_dpe] = {
                        "nb_transactions": int(row.nb_transactions),
                        "prix_m2_moyen": float(row.prix_m2_moyen) if row.prix_m2_moyen else 0.0,
                        "prix_m2_min": float(row.prix_m2_min) if row.prix_m2_min else 0.0,
                        "prix_m2_max": float(row.prix_m2_max) if row.prix_m2_max else 0.0
                    }
                    
                    # 4. On calcule le nb de transactions par type de bien
                    cp_communes[code_postal]["types_biens"][type_bien_row]["total_transactions_type"] += int(row.nb_transactions)
                    
                    # 5. On calcule le nb de transactions par commune
                    cp_communes[code_postal]["total_transactions_commune"] += int(row.nb_transactions)
                    
                    # 6. puis sur l'ensemble
                    total_transactions += int(row.nb_transactions)
                    
                    if row.prix_m2_moyen:
                        prix_global.extend([float(row.prix_m2_moyen)] * int(row.nb_transactions))

                # 7. On Calcul du prix moyen par type de bien et par commune
                for code_postal, commune_data in cp_communes.items():
                    commune_prix = []
                    
                    for type_bien_key, type_data in commune_data["types_biens"].items():
                        type_prix = []
                        
                        # Prix moyen par type de bien basé sur les étiquettes DPE
                        for etiquette, stats in type_data["etiquettes_dpe"].items():
                            if stats["prix_m2_moyen"] > 0:
                                # Pondération par nombre de transactions
                                type_prix.extend([stats["prix_m2_moyen"]] * stats["nb_transactions"])
                                commune_prix.extend([stats["prix_m2_moyen"]] * stats["nb_transactions"])
                        
                        # Prix moyen par type de bien
                        type_data["prix_m2_moyen_type"] = round(
                            sum(type_prix) / len(type_prix) if type_prix else 0, 2
                        )
                    
                    # Prix moyen par commune
                    commune_data["prix_m2_moyen_commune"] = round(
                        sum(commune_prix) / len(commune_prix) if commune_prix else 0, 2
                    )

                # 7. On calcule le prix global sur l'ensemble de stransactions recueillies
                prix_global_moyen = sum(prix_global) / len(prix_global) if prix_global else 0.0
                
                # On contruit le resultat final
                result = {
                    "code_insee": code_insee,
                    "total_transactions": total_transactions,
                    "prix_m2_global_moyen": round(prix_global_moyen, 2),
                    "nb_communes": len(cp_communes),
                    "communes": cp_communes,
                    "metadata": {
                        "filtres_appliques": {
                            "type_bien": type_bien,
                            "surface_min": surface_min,
                            "surface_max": surface_max,
                            "etiquette_dpe": etiquette_dpe
                        }
                    }
                }
                
                return success_response(
                    data=result,
                    message=f"Évaluation du code INSEE {code_insee} réussie avec {total_transactions} transactions dans {len(cp_communes)} communes.",
                    count=total_transactions,
                )
                
        except Exception as e:
            return error_response(
                message=f"Erreur lors de l'analyse du code INSEE {code_insee}: {str(e)}",
                error_code="DATABASE_ERROR",
                details={
                    "code_insee": code_insee,
                    "type_bien": type_bien,
                    "surface_min": surface_min,
                    "surface_max": surface_max,
                    "etiquette_dpe": etiquette_dpe,
                    "error_message": etiquette_dpe,
                    "error_type": type(e).__name__
                }
            )
        
    @staticmethod
    def display_city_first_ring(code_insee: str) -> dict:
        """
        Affiche les villes du premier anneau autour d'une ville donnée
        Args:
            code_insee (str): Code INSEE de la ville centrale
        Returns:
            dict: Dictionnaire contenant les villes du premier anneau
        """
        # Requête simple pour prix moyen au m2 d'un code INSEE
        sql_request = """
        SELECT ROUND(AVG(t.valeur_fonciere::numeric / NULLIF(bi.surface_reelle_bati, 0)), 2) as prix_m2_moyen
        FROM transaction_dvf t
        JOIN bien_immobilier bi ON t.id_bien = bi.id_bien
        JOIN commune c ON bi.id_commune = c.id_commune
        WHERE c.code_insee_commune = :code_insee_commune
        AND bi.surface_reelle_bati > 0
        AND t.valeur_fonciere > 0
        """
        commune_name = None

        try:
            commune_name = commune_graph_service.get_commune_name_by_code_insee(code_insee)
            limitrophes = commune_graph_service.get_communes_limitrophes(code_insee)
            
            if not limitrophes:
                return error_response(
                    message=f"Aucune commune limitrophe trouvée pour {commune_name}",
                    error_code="NO_LIMITROPHES_FOUND"
                )
            
            with get_session_sync() as session:
                
                result_central = session.connection().execute(
                    text(sql_request), 
                    {"code_insee_commune": code_insee}
                ).first()
                commune_central_prix_moyen = float(result_central.prix_m2_moyen) if result_central and result_central.prix_m2_moyen else 0.0
                
                communes_avec_prix = []
                for commune in limitrophes:
                    
                    result = session.connection().execute(
                        text(sql_request), 
                        {"code_insee_commune": commune["code_commune"]}
                    ).first()
                    
                    prix_moyen = float(result.prix_m2_moyen) if result and result.prix_m2_moyen else 0.0
                    
                    communes_avec_prix.append({
                        "nom": commune["nom"],
                        "code_commune": commune["code_commune"],
                        "direction": commune["direction"],
                        "prix_m2_moyen": prix_moyen
                    })

            return success_response(
                data={
                    "commune_centrale": commune_name,
                    "prix_m2_moyen": commune_central_prix_moyen,
                    "communes_limitrophes": communes_avec_prix
                },
                message=f"Premier anneau de {commune_name} récupéré avec succès.",
                count=len(communes_avec_prix)
            )
        
        except Exception as e:
            return error_response(
                message=f"Erreur lors de la récupération des communes limitrophes pour la commune de {commune_name}, code INSEE {code_insee}: {str(e)}",
                error_code="DATABASE_ERROR",
                details={
                    "code_insee": code_insee,
                    "error_message": str(e),
                    "error_type": type(e).__name__
                }
            )