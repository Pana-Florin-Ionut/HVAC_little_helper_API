        # columns=("client_id, project_id, offer_name"),
        # columns=", ".join(str(x) for x in columns if x != "id"),
        # values=tuple(str(x) for x in values if x != None),



    #     logging.error(f"offer {offer_name} does not exist + {e}")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail=f"offer {offer_name} does not exist")
    # except psycopg2.errors.UndefinedTable as e:
    #     logging.error(f"offer {offer_name} does not exist + {e}")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail=f"offer {offer_name} does not exist B")


# @router.post("/")
# def create_offer(
#     offer: schemas.Offers,
# ):
#     # database_connection.execute_query2(query)
#     try:
#         query = db.make_table(offer.offer_name)
#         db.create_table(query)
#         # return {f"{offer}": f"{offer_name}"}
#         return {"message": f"{offer.offer_name} created"}
#     except Exception as e:
#         print(e)
#         return {"message": e}


# @router.get("/offer/{offer_name}")
# def get_offer(
#     offer_name,
# ):
#     offer = db.get_table(f"SELECT * FROM {offer_name}")



 # try:
    #     # check if the offer table exists
    #     db.execute(text(tables.get_offer(offer_name))).first()
    #     # get the offer details
    #     offer = get_offer_details(offer_name, db)
    #     # get the products
    #     products = db.query(table_models_required.Products).filter(
    #         table_models_required.Products.offer_id == offer.offer_id
    #     ).all()
    #     return products
    # except sqlalchemy.exc.ProgrammingError as e:
    #     if e.orig.pgcode == "42P01":
    #         # check if the offer table exists
    #         logging.error(
    #             f"{datetime.utcnow()} {offer_name}: Internal Server Error + {e}"
    #         )
    #         raise HTTPException(: