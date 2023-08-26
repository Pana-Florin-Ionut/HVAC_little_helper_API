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


# logging.warn(f"{datetime.utcnow()} - Error creating user: {e} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.pgcode} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.pgerror} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.diag.message_detail} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.diag.message_hint} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.diag.statement_position} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.diag.internal_position} ")
# logging.warn(f"{datetime.utcnow()} - Error creating user: {e.orig.diag.internal_query})


# class TestProduct(Base):
#     __tablename__ = "test_products"
#     id = Column(Integer, index=True, primary_key=True)
#     company_id = Column(
#         Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
#     )
#     product_name = Column(String, nullable=False)
#     details = Column(String, nullable=True)
#     created = Column(
#         TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
#     )
#     UniqueConstraint(company_id, product_name)


# @router.get(
#     "", status_code=status.HTTP_200_OK, response_model=list[prices_schemas.PricesOut]
# )
# def get_prices(
#     db: Session = Depends(get_db),
#     user: users_schemas.UserOut = Depends(oauth2.get_current_user),
# ):
#     """
#     Get all prices.
#     """
#     prices = db.query(table_models_required.OfferPrices).all()
#     return prices

# From routers.prices
# def create_product_with_prices(
#     product: products_schemas.ProductOut, price: prices_schemas.PricesOut
# ) -> prices_schemas.ProductWithPrices:
#     print(product.to_dict())
#     product_with_prices = prices_schemas.ProductWithPrices(
#         id=product.id,
#         offer_id=product.offer_id,
#         product_key=product.product_key,
#         product_name=product.product_name,
#         ch_1=product.ch_1,
#         ch_2=product.ch_2,
#         ch_3=product.ch_3,
#         ch_4=product.ch_4,
#         ch_5=product.ch_5,
#         ch_6=product.ch_6,
#         ch_7=product.ch_7,
#         ch_8=product.ch_8,
#         um=product.um,
#         quantity=product.quantity,
#         created_by=product.created_by,
#         created=product.created,
#         owner=product.owner,
#         offering_company=price.offering_company,
#         offer_product_id=price.offer_product_id,
#         price=price.price,
#     )
#     # product_with_prices = prices_schemas.ProductWithPrices(product, price)
#     return product_with_prices


# @router.get(
#     "",
#     status_code=status.HTTP_200_OK,
#     response_model=list[prices_schemas.ProductWithPrices],
# )
# async def get_product_prices(
#     db: Session = Depends(get_db),
#     user: users_schemas.UserOut = Depends(oauth2.get_current_user),
# ):
#     match user.role:
#         case users_schemas.Roles.app_admin:
#             query = select(
#                 table_models_required.OffersBody,
#                 table_models_required.OfferPrices,
#             ).join(table_models_required.OfferPrices)
#             response = db.execute(query).all()
#             final_response = []
#             for resp in response:
#                 product = resp[0]
#                 price = resp[1]
#                 product_with_prices = create_product_with_prices(product, price)
#                 final_response.append(product_with_prices)
#             return final_response
#         case users_schemas.Roles.admin | users_schemas.Roles.user | users_schemas.Roles.manager:
#             query = (
#                 select(
#                     table_models_required.OffersBody,
#                     table_models_required.OfferPrices,
#                 )
#                 .join(table_models_required.OfferPrices)
#                 .where(
#                     table_models_required.OffersBody.offer.has(
#                         table_models_required.Offers.company_key == user.company_key
#                     )
#                 )
#             )
#             response = db.execute(query).all()
#             final_response = []
#             for resp in response:
#                 product = resp[0]
#                 price = resp[1]
#                 product_with_prices = create_product_with_prices(product, price)
#                 final_response.append(product_with_prices)
#             return final_response
#         case users_schemas.Roles.custom:
#             if not user_permissions.can_view_offer(user.id, db):
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
#                 )
#             query = (
#                 select(
#                     table_models_required.OffersBody,
#                     table_models_required.OfferPrices,
#                 )
#                 .join(table_models_required.OfferPrices)
#                 .where(
#                     table_models_required.OffersBody.offer.has(
#                         table_models_required.Offers.company_key == user.company_key
#                     )
#                 )
#             )
#             response = db.execute(query).all()
#             final_response = []
#             for resp in response:
#                 product = resp[0]
#                 price = resp[1]
#                 product_with_prices = create_product_with_prices(product, price)
#                 final_response.append(product_with_prices)
#             return final_response
