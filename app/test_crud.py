
from .database import get_session, create_db_and_tables, engine
from sqlmodel import Session
from .models import BienImmobilierBase, CommuneCreate
from .crud import bien_immobilier_crud, commune_crud

def main():
    print("=== Test des fonction CRUD ===")
    print("_"* 50)
    print("=== Test des fonction crud.commune ===")
    
    with Session(engine) as session:
        print("=== TEST: creation d'une commune ===")
        commune_data = CommuneCreate(
            code_insee_commune="75056",
            nom_commune="Paris",
            code_postal="75001",
        )
        if not commune_crud.get_by_code_insee(session, commune_data.code_insee_commune):
            created_commune = commune_crud.create(session, commune_data)
            print("Commune créée:", created_commune)
        else:
            print("La commune existe déjà, pas de création.")
        input("Appuyez sur Entrée pour continuer...")


        print("=== TEST: get_all_communes ===")
        communes = commune_crud.get_all_communes(session)
        print(f"{len(communes)} commune(s) trouvée(s)")
        input("Appuyez sur Entrée pour continuer...")


        print("=== TEST: create bien immobilier===")
        bien_data = BienImmobilierBase(
            adresse_normalisee="12 rue de la République",
            code_insee_commune="75056",
            type_bien="Appartement",
            surface_reelle_bati=55
        )
        created = bien_immobilier_crud.create(session, bien_data)
        print("Créé:", created)
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: get_by_id ===")
        bien = bien_immobilier_crud.get_by_id(session, created.id_bien)
        print("Récupéré:", bien)
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: get_all ===")
        biens = bien_immobilier_crud.get_all(session)
        print(f"{len(biens)} bien(s) trouvé(s)")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: get_by_commune ===")
        biens_commune = bien_immobilier_crud.get_by_commune(session, "75056")
        print(f"{len(biens_commune)} bien(s) dans la commune 75056")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: get_by_type ===")
        biens_type = bien_immobilier_crud.get_by_type(session, "Appartement")
        print(f"{len(biens_type)} appartement(s) trouvé(s)")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: get_by_surface_range ===")
        biens_surface = bien_immobilier_crud.get_by_surface_range(session, 50, 60)
        print(f"{len(biens_surface)} bien(s) entre 50 et 60 m²")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: search_by_address ===")
        biens_adresse = bien_immobilier_crud.search_by_address(session, "République")
        print(f"{len(biens_adresse)} bien(s) avec 'République' dans l'adresse")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: update ===")
        update_data = BienImmobilierBase(surface_reelle_bati=60)
        updated = bien_immobilier_crud.update(session, created.id_bien, update_data)
        print("Mis à jour:", updated)
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: count ===")
        total = bien_immobilier_crud.count(session)
        print(f"Nombre total de biens: {total}")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: count_by_commune ===")
        count_commune = bien_immobilier_crud.count_by_commune(session, "75056")
        print(f"Nombre de biens dans 75056: {count_commune}")
        input("Appuyez sur Entrée pour continuer...")

        print("\n=== TEST: delete ===")
        deleted = bien_immobilier_crud.delete(session, created.id_bien)
        print("Supprimé:", deleted)
        input("Appuyez sur Entrée pour terminer.")



if __name__ == "__main__":
    main()