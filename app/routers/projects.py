from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.routers.renaming import update_projects
from .. import schemas, table_models_required
from ..database import get_db
from .. import oauth2
from sqlalchemy import update
from .utils import check_company_exists, check_company_has_projects, get_company_details
import sqlalchemy
from .. import user_permissions

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

# company_key is the company key


@router.get("", status_code=status.HTTP_200_OK, response_model=list[schemas.Project])
def get_projects(
    user: schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    company_key: Optional[str] = None,
    company_id: Optional[int] = None,
    project_name: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    match user.role:
        case "application_administrator":
            try:
                query = select(table_models_required.Projects)
                if company_id is not None:
                    query = query.where(
                        table_models_required.Projects.company_id == company_id
                    )
                if search is not None:
                    query = query.where(
                        table_models_required.Projects.project_name.icontains(search)
                    )
                if company_key is not None:
                    query = query.where(
                        table_models_required.Projects.project_name.icontains(
                            company_key
                        )
                    )
                query = query.limit(limit).offset(offset)
                print(query)
                projects = db.scalars(query).all()

                return projects
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project not found",
                )
        case "test_user":
            try:
                query = (
                    select(table_models_required.Projects)
                    .where(
                        table_models_required.Projects.project_name.icontains(
                            company_key
                        )
                    )
                    .where(
                        table_models_required.Projects.project_name.icontains(
                            project_name
                        )
                    )
                )
                if company_id is not None:
                    query = query.where(
                        table_models_required.Projects.company_id == company_id
                    )
                query = query.limit(limit).offset(offset)

                projects = db.scalars(query).all()

                return projects
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with key  does not exist",
                )
        case "admin", "manager", "user":
            try:
                query = (
                    select(table_models_required.Projects)
                    .where(table_models_required.Projects.company_id == user.company_id)
                    .where(
                        table_models_required.Projects.project_name.icontains(
                            company_key
                        )
                    )
                )
                if company_id is not None:
                    query = query.where(
                        table_models_required.Projects.company_id == company_id
                    )
                query = query.limit(limit).offset(offset)
                projects = db.scalars(query).all()

                return projects
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with key  does not exist",
                )
        case "custom":
            if user_permissions.can_view_project(user.id, db):
                try:
                    query = (
                        select(table_models_required.Projects)
                        .where(
                            table_models_required.Projects.company_id == user.company_id
                        )
                        .where(
                            table_models_required.Projects.project_name.icontains(
                                company_key
                            )
                        )
                    )
                    if company_id is not None:
                        query = query.where(
                            table_models_required.Projects.company_id == company_id
                        )
                    projects = db.scalars(query).all()

                    return projects
                except Exception as e:
                    print(e)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Company with key  does not exist",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authorized to view this project",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to view this project",
            )


@router.post("/")
def create_project():
    return {"message": "create project"}
