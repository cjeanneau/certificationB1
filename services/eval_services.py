from typing import Optional
from bddpg import get_session_sync, BienImmobilier, TransactionDVF, DPE
from sqlmodel import select, desc

class EvalServices:
   
    
    @staticmethod
    def eval_multifields_cp_bak(
        cp: str,
        type_bien: Optional[str] = None,
        surface_min: Optional[float] = None,
        surface_max: Optional[float] = None,
        etiquette_dpe: Optional[int] = None
    ) -> float:
        """
        Evaluation immobilière (prix au m2) avancée par code postal.
        
        Args:
            cp (str) : Code postal à évaluer.
            type_bien (Optional[str]) : Type de bien immobilier.
            surface_min (Optional[float]) : Surface minimale du bien.
            surface_max (Optional[float]) : Surface maximale du bien.
            etiquette_dpe (Optional[int]) : Etiquette DPE du bien.

        Returns:
            float: Résultat de l'évaluation immobilière.
        """
        #  Cette méthode interroge la BDD postGreSQL pour obtenir les données nécessaires à l'évaluation.
        
        # On vérifie la présnce d'un code postal valide
        if not cp or len(cp) != 5 or not cp.isdigit():
            raise ValueError("Le code postal doit être une chaîne de 5 chiffres.")
        
        # si seulement cp présent alors on interroge la BDD pour récupérer les données
        # et on calcule le prix au m2 moyen pour le code postal donné.
        # Si d'autres champs sont présents, on les utilise pour affiner la recherche.

        
        try:
            with get_session_sync() as session:
                
                # 🎯 Construction de la requête avec TOUS les filtres d'un coup
                query = select(
                    BienImmobilier.id_bien,
                    BienImmobilier.code_postal,
                    BienImmobilier.type_bien,
                    DPE.surface_habitable_logement,
                    DPE.etiquette_dpe,
                    TransactionDVF.valeur_fonciere,
                    TransactionDVF.date_mutation
                ).select_from(
                    BienImmobilier
                    .join(DPE, BienImmobilier.id_bien == DPE.id_bien)
                    .join(TransactionDVF, BienImmobilier.id_bien == TransactionDVF.id_bien)
                ).where(
                    # ✅ Filtre obligatoire : Code postal
                    BienImmobilier.code_postal == cp,
                    # ✅ Filtre obligatoire : Surface valide (> 0)
                    DPE.surface_habitable_logement > 0,
                    # ✅ Filtre obligatoire : Valeur foncière valide
                    TransactionDVF.valeur_fonciere > 0
                )
                
                # ✅ Ajouter les filtres optionnels selon leur présence
                if type_bien:
                    query = query.where(BienImmobilier.type_bien == type_bien)
                
                if surface_min is not None:
                    query = query.where(DPE.surface_habitable_logement >= surface_min)
                
                if surface_max is not None:
                    query = query.where(DPE.surface_habitable_logement <= surface_max)
                
                if etiquette_dpe is not None:
                    query = query.where(DPE.etiquette_dpe == etiquette_dpe)
                
                # ✅ Ordonner par date pour récupérer les dernières transactions
                query = query.order_by(desc(TransactionDVF.date_mutation))
                
                # Exécuter la requête
                results = session.exec(query).all()
                
                if not results:
                    raise ValueError(f"Aucun bien trouvé pour les critères donnés dans le CP {cp}")
                
                r# 💰 Calculer directement les prix au m²
                prix_m2_list = [
                    row.valeur_fonciere / row.surface_habitable_logement 
                    for row in results
                ]
                
                prix_m2_moyen = sum(prix_m2_list) / len(prix_m2_list)
                
                print(f"✅ Évaluation optimisée {cp}: {len(prix_m2_list)} biens")
                print(f"📊 Prix au m² moyen : {prix_m2_moyen:.2f}€")
                
                return round(prix_m2_moyen, 2)
                
        except Exception as e:
            raise ValueError("Erreur lors de l'évaluation immobilière : {str(e)}")        



    @staticmethod
    def eval_multifields_cp(
        cp: str,
        type_bien: Optional[str] = None,
        surface_min: Optional[float] = None,
        surface_max: Optional[float] = None,
        etiquette_dpe: Optional[int] = None
    ) -> float:
        """Version avec SQL brut pour performance maximale"""
        
        if not cp or len(cp) != 5 or not cp.isdigit():
            raise ValueError("Le code postal doit être une chaîne de 5 chiffres.")
        
        try:
            with get_session_sync() as session:
                
                # 🎯 Construction dynamique de la requête SQL
                base_sql = """
                SELECT 
                    AVG(dt.valeur_fonciere / d.surface_habitable_logement) as prix_m2_moyen,
                    COUNT(*) as nb_biens
                FROM bien_immobilier bi
                JOIN dpe d ON bi.id_bien = d.id_bien
                JOIN (
                    SELECT DISTINCT ON (id_bien) 
                        id_bien, 
                        valeur_fonciere, 
                        date_mutation
                    FROM transaction_dvf
                    WHERE valeur_fonciere > 0
                    ORDER BY id_bien, date_mutation DESC
                ) dt ON bi.id_bien = dt.id_bien
                WHERE bi.code_postal = :cp
                AND d.surface_habitable_logement > 0
                """
                
                # ✅ Ajouter les conditions dynamiquement
                conditions = []
                params = {"cp": cp}
                
                if type_bien:
                    conditions.append("AND bi.type_bien = :type_bien")
                    params["type_bien"] = type_bien
                    
                if surface_min is not None:
                    conditions.append("AND d.surface_habitable_logement >= :surface_min")
                    params["surface_min"] = surface_min
                    
                if surface_max is not None:
                    conditions.append("AND d.surface_habitable_logement <= :surface_max")
                    params["surface_max"] = surface_max
                    
                if etiquette_dpe is not None:
                    conditions.append("AND d.etiquette_dpe = :etiquette_dpe")
                    params["etiquette_dpe"] = etiquette_dpe
                
                # Construire la requête finale
                final_sql = base_sql + " ".join(conditions)
                
                # Exécuter
                result = session.exec(text(final_sql), params).first()
                
                if not result or result.nb_biens == 0:
                    raise ValueError(f"Aucun bien trouvé pour les critères dans le CP {cp}")
                
                prix_m2_moyen = float(result.prix_m2_moyen)
                
                print(f"✅ Évaluation SQL {cp}: {result.nb_biens} biens")
                print(f"📊 Prix au m² moyen: {prix_m2_moyen:.2f}€")
                
                return round(prix_m2_moyen, 2)
                
        except Exception as e:
            raise ValueError(f"Erreur lors de l'évaluation: {str(e)}")

        
        