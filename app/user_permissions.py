from . import table_models_required
from fastapi import HTTPException, status
from sqlalchemy.orm import Session




def can_create_project(user_id: int, dbx: Session):
    create_project_permission = dbx.query(table_models_required.Roles).filter(table_models_required.Roles.user_id == user_id).first()
    print(create_project_permission.can_create_project)
    return create_project_permission.can_create_project

# can_create_project(1, db)

# def check_user_permissions(offer_name: str, user: schemas.UserOut, db: Session):
#     user = (
#         db.query(table_models_required.Users)
#         .filter(table_models_required.Users.id == id)
#         .first()
#     )
#     if user.role in db.query(table_models_required.Roles).where(table_models_required.Roles.user_id == user.id).first():
#         return True
#     elif user.role == "administrator":
#         return True
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
#         )
