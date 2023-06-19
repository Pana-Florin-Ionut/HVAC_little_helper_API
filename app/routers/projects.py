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
    project_key: Optional[int] = None,
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
                if project_key is not None:
                    query = query.where(
                        table_models_required.Projects.project_key.icontains(
                            project_key
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
        case "admin" | "manager" | "user":
            try:
                query = select(table_models_required.Projects).where(
                    table_models_required.Projects.company_id == user.company_id
                )
                if search is not None:
                    query = query.where(
                        table_models_required.Projects.project_name.icontains(search)
                    )
                if project_name is not None:
                    query = query.where(
                        table_models_required.Projects.project_name.icontains(
                            project_name
                        )
                    )
                if project_key is not None:
                    query = query.where(
                        table_models_required.Projects.project_key.icontains(
                            project_key
                        )
                    )
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
                    query = select(table_models_required.Projects).where(
                        table_models_required.Projects.company_id == user.company_id
                    )
                    if search is not None:
                        query = query.where(
                            table_models_required.Projects.project_name.icontains(
                                search
                            )
                        )
                    if project_name is not None:
                        query = query.where(
                            table_models_required.Projects.project_name.icontains(
                                project_name
                            )
                        )
                    if project_key is not None:
                        query = query.where(
                            table_models_required.Projects.project_key.icontains(
                                project_key
                            )
                        )
                    projects = db.scalars(query).all()

                    return projects
                except Exception as e:
                    print(e)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Projects not found",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authorized to view this project",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to view projects",
            )


@router.post(
    "/admin", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED
)
def create_project(
    project: schemas.ProjectCreateAdmin,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case "application_administrator":
            try:
                print(project)
                db_project = table_models_required.Projects(
                    created_by=user.id, **project.dict()
                )
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                return db.scalars(select(table_models_required.Projects).where(
                    table_models_required.Projects.project_key == db_project.project_key
                )).first()
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with key  does not exist",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to create projects as an admin",
            )


router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)


def create_project(
    project: schemas.ProjectCreateUser,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case "admin" | "manager" | "user":
            try:
                db_project: dict = table_models_required.Projects(
                    created_by=user.id, company_id=user.company_id, **project.dict()
                )
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                return db_project
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with key  does not exist",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to create projects as an admin",
            )
