# services/statistics.py
from sqlmodel import Session, select, func
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
from ..models.bien_immobilier import BienImmobilier
from ..models.transaction_dvf import TransactionDVF
from ..models.dpe import DPE
from ..models.commune import Commune

class StatisticsService:
    """Service pour les statistiques immobilières"""
    
    def get_global_stats(self, session: Session) -> Dict:
        """Retourne les statistiques globales"""
        # Nombre total de biens
        nb_biens = len(list(session.exec(select(BienImmobilier)).all()))
        
        # Nombre total de transactions
        nb_transactions = len(list(session.exec(select(TransactionDVF)).all()))
        
        # Nombre total de DPE
        nb_dpe = len(list(session.exec(select(DPE)).all()))
        
        # Nombre total de communes
        nb_communes = len(list(session.exec(select(Commune)).all()))
        
        # Prix moyen des transactions
        avg_price_result = session.exec(
            select(func.avg(TransactionDVF.valeur_fonciere)).where(
                TransactionDVF.valeur_fonciere.is_not(None)
            )
        ).first()
        prix_moyen = Decimal(str(avg_price_result)) if avg_price_result else None
        
        return {
            "nombre_biens": nb_biens,
            "nombre_transactions": nb_transactions,
            "nombre_dpe": nb_dpe,
            "nombre_communes": nb_communes,
            "prix_moyen_transaction": float(prix_moyen) if prix_moyen else None
        }
    
    def get_price_evolution(self, session: Session, months: int = 12) -> List[Dict]:
        """Retourne l'évolution des prix sur les derniers mois"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        # Grouper par mois
        statement = select(
            func.date_trunc('month', TransactionDVF.date_mutation).label('mois'),
            func.avg(TransactionDVF.valeur_fonciere).label('prix_moyen'),
            func.count(TransactionDVF.id_transaction).label('nb_transactions')
        ).where(
            TransactionDVF.date_mutation >= start_date,
            TransactionDVF.valeur_fonciere.is_not(None)
        ).group_by(
            func.date_trunc('month', TransactionDVF.date_mutation)
        ).order_by('mois')
        
        results = session.exec(statement).all()
        
        return [
            {
                "mois": row.mois.strftime("%Y-%m"),
                "prix_moyen": float(row.prix_moyen),
                "nb_transactions": row.nb_transactions
            }
            for row in results
        ]
    
    def get_stats_by_type_bien(self, session: Session) -> Dict:
        """Retourne les statistiques par type de bien"""
        statement = select(
            BienImmobilier.type_bien,
            func.count(BienImmobilier.id_bien).label('count'),
            func.avg(BienImmobilier.surface_reelle_bati).label('surface_moyenne')
        ).where(
            BienImmobilier.type_bien.is_not(None)
        ).group_by(BienImmobilier.type_bien)
        
        results = session.exec(statement).all()
        
        return {
            row.type_bien: {
                "nombre": row.count,
                "surface_moyenne": float(row.surface_moyenne) if row.surface_moyenne else None
            }
            for row in results
        }
    
    def get_stats_by_commune(self, session: Session, limit: int = 10) -> List[Dict]:
        """Retourne les statistiques par commune (top communes)"""
        statement = select(
            Commune.nom_commune,
            Commune.code_insee_commune,
            func.count(BienImmobilier.id_bien).label('nb_biens'),
            func.count(TransactionDVF.id_transaction).label('nb_transactions')
        ).select_from(
            Commune
        ).join(
            BienImmobilier, Commune.code_insee_commune == BienImmobilier.code_insee_commune
        ).outerjoin(
            TransactionDVF, BienImmobilier.id_bien == TransactionDVF.id_bien
        ).group_by(
            Commune.nom_commune, Commune.code_insee_commune
        ).order_by(
            func.count(BienImmobilier.id_bien).desc()
        ).limit(limit)
        
        results = session.exec(statement).all()
        
        return [
            {
                "nom_commune": row.nom_commune,
                "code_insee": row.code_insee_commune,
                "nb_biens": row.nb_biens,
                "nb_transactions": row.nb_transactions or 0
            }
            for row in results
        ]
    
    def get_dpe_distribution(self, session: Session) -> Dict:
        """Retourne la distribution des étiquettes DPE"""
        # Distribution DPE
        statement_dpe = select(
            DPE.etiquette_dpe,
            func.count(DPE.id_dpe).label('count')
        ).where(
            DPE.etiquette_dpe.is_not(None)
        ).group_by(DPE.etiquette_dpe)
        
        results_dpe = session.exec(statement_dpe).all()
        
        # Distribution GES
        statement_ges = select(
            DPE.etiquette_ges,
            func.count(DPE.id_dpe).label('count')
        ).where(
            DPE.etiquette_ges.is_not(None)
        ).group_by(DPE.etiquette_ges)
        
        results_ges = session.exec(statement_ges).all()
        
        return {
            "dpe": {row.etiquette_dpe: row.count for row in results_dpe},
            "ges": {row.etiquette_ges: row.count for row in results_ges}
        }
    
    def get_price_stats_by_surface(self, session: Session) -> List[Dict]:
        """Retourne les statistiques de prix par tranche de surface"""
        # Définir les tranches de surface
        tranches = [
            (0, 50, "0-50m²"),
            (50, 100, "50-100m²"),
            (100, 150, "100-150m²"),
            (150, 200, "150-200m²"),
            (200, float('inf'), "200m²+")
        ]
        
        results = []
        for min_surf, max_surf, label in tranches:
            if max_surf == float('inf'):
                condition = BienImmobilier.surface_reelle_bati >= min_surf
            else:
                condition = (BienImmobilier.surface_reelle_bati >= min_surf) & \
                           (BienImmobilier.surface_reelle_bati < max_surf)
            
            statement = select(
                func.avg(TransactionDVF.valeur_fonciere).label('prix_moyen'),
                func.count(TransactionDVF.id_transaction).label('nb_transactions')
            ).select_from(
                TransactionDVF
            ).join(
                BienImmobilier, TransactionDVF.id_bien == BienImmobilier.id_bien
            ).where(
                condition,
                TransactionDVF.valeur_fonciere.is_not(None),
                BienImmobilier.surface_reelle_bati.is_not(None)
            )
            
            result = session.exec(statement).first()
            
            if result and result.nb_transactions > 0:
                results.append({
                    "tranche_surface": label,
                    "prix_moyen": float(result.prix_moyen),
                    "nb_transactions": result.nb_transactions
                })
        
        return results
    
    def get_market_trends(self, session: Session, commune_code: Optional[str] = None) -> Dict:
        """Retourne les tendances du marché"""
        base_query = select(TransactionDVF).where(
            TransactionDVF.valeur_fonciere.is_not(None)
        )
        
        if commune_code:
            base_query = base_query.join(
                BienImmobilier, TransactionDVF.id_bien == BienImmobilier.id_bien
            ).where(
                BienImmobilier.code_insee_commune == commune_code
            )
        
        # Période actuelle (6 derniers mois)
        six_months_ago = datetime.now().date() - timedelta(days=180)
        current_period = base_query.where(
            TransactionDVF.date_mutation >= six_months_ago
        )
        
        # Période précédente (6 mois avant)
        twelve_months_ago = datetime.now().date() - timedelta(days=360)
        previous_period = base_query.where(
            TransactionDVF.date_mutation >= twelve_months_ago,
            TransactionDVF.date_mutation < six_months_ago
        )
        
        # Prix moyen période actuelle
        current_avg = session.exec(
            select(func.avg(TransactionDVF.valeur_fonciere)).select_from(current_period.subquery())
        ).first()
        
        # Prix moyen période précédente
        previous_avg = session.exec(
            select(func.avg(TransactionDVF.valeur_fonciere)).select_from(previous_period.subquery())
        ).first()
        
        # Calcul de la tendance
        if current_avg and previous_avg and previous_avg > 0:
            evolution = ((current_avg - previous_avg) / previous_avg) * 100
        else:
            evolution = 0
        
        return {
            "prix_moyen_actuel": float(current_avg) if current_avg else None,
            "prix_moyen_precedent": float(previous_avg) if previous_avg else None,
            "evolution_pourcentage": round(evolution, 2),
            "tendance": "hausse" if evolution > 0 else "baisse" if evolution < 0 else "stable"
        }

# Instance globale
statistics_service = StatisticsService()