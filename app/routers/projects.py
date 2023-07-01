from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from .. import schemas, table_models_required
from ..database import get_db
from .. import oauth2
from sqlalchemy import update
from .utils import (
    get_project_details_Co_id,
    project_exists_key,
    check_project_exists_name,
    check_project_exists_key,
    get_project_details_Co_key,
    project_exists_name,
)
import sqlalchemy
from .. import user_permissions

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

# company_key is the company key
#


@router.get("", status_code=status.HTTP_200_OK, response_model=list[schemas.ProjectOut])
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
                # print(f"QUERY: {query}")
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
                # print(query)
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


@router.post("", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
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
            except sqlalchemy.exc.IntegrityError as e:
                # e.orig.pgcode == "23505" is the error code for unique constraint violation
                if e.orig.pgcode == "23505":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Project with name {project.project_name} already exists",
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Internal server error",
                    )
        case "custom":
            if user_permissions.can_create_project(user.id, db):
                try:
                    db_project: dict = table_models_required.Projects(
                        created_by=user.id, company_id=user.company_id, **project.dict()
                    )
                    db.add(db_project)
                    db.commit()
                    db.refresh(db_project)
                    return db_project
                except sqlalchemy.exc.IntegrityError as e:
                    # e.orig.pgcode == "23505" is the error code for unique constraint violation
                    if e.orig.pgcode == "23505":
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=f"Project with name {project.project_name} already exists",
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error",
                        )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to create projects as an admin",
            )


@router.post(
    "/admin", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED
)
def create_project(
    project: schemas.ProjectCreateAdmin,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    # company_details = get
    # new_project_name =
    # if project_exists_name(project.project_name, db):
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=f"Project with name {project.project_name} already exists",
    #     )
    # if project_exists_key(project.project_key, db):
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=f"Project with key {project.project_key} already exists",
    #     )
    match user.role:
        case "application_administrator":
            try:
                # print(project)
                db_project = table_models_required.Projects(
                    created_by=user.id, **project.dict()
                )
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                project = get_project_details_Co_id(
                    db_project.project_key, db_project.company_id, db
                )
                return project
            except sqlalchemy.exc.IntegrityError as e:
                # print(e.orig.pgcode)
                if e.orig.pgcode == "23505":
                    # e.orig.pgcode == "23505" is the error code for unique constraint violation
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Project with name {project.project_name} or key {project.project_key} already exists ",
                    )
                elif e.orig.pgcode == "23503":
                    # 23503 pgcode is psycopg2.errors.ForeignKeyViolation
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Company with id {project.company_id} does not exist",
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Error creating project, please check your inputs",
                    )
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error creating project, please check your inputs",
                )

        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to create projects as an admin",
            )


@router.put(
    "/admin/{company_key}/{project_key}",
    response_model=schemas.ProjectOut,
    status_code=status.HTTP_200_OK,
)
def update_project(
    company_key: str,
    project_key: str,
    project: schemas.ProjectUpdateAdmin,
    user: schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    match user.role:
        case "application_administrator":
            try:
                # if get_project_details(project_key, db) is None:
                #     raise HTTPException(
                #         status_code=status.HTTP_404_NOT_FOUND,
                #         detail=f"Project with key {project_key} does not exist",
                #     )
                if not project_exists_key(project_key, company_key, db):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Project with key {project_key} for company {company_key} does not exist",
                    )

                query = (
                    update(table_models_required.Projects)
                    .where(table_models_required.Projects.project_key == project_key)
                    .filter(
                        table_models_required.Projects.company.has(
                            company_key=company_key
                        )
                    )
                    # .filter(table_models_required.Companies.company_key == company_key)
                    .values(**project.dict())
                )
                # print(query)
                db.execute(query)
                db.commit()
                project = get_project_details_Co_key(project_key, company_key, db)
                return project
            except sqlalchemy.exc.IntegrityError as e:
                # print(e)
                # e.orig.pgcode == "23505" is the error code for unique constraint violation
                if e.orig.pgcode == "23505":
                    print("origin")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Project with name {project.project_name}  already exists ",
                    )

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error creating project, please check your inputs",
                )


@router.get("/admin/{project_key}")
def get_project_test(
    project_key: str,
    db: Session = Depends(get_db),
):
    if project_exists_key(project_key, db):
        return {"message": "Project exists"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with key {project_key} does not exist",
        )


@router.delete("/{project_key}", status_code=status.HTTP_200_OK)
def delete_project(
    project_key: str,
    db: Session = Depends(get_db),
    user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    match user.role:
        case "application_administrator":
            if not project_exists_key(project_key, db):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with key {project_key} does not exist",
                )
            try:
                query = delete(table_models_required.Projects).where(
                    table_models_required.Projects.project_key == project_key
                )
                db.execute(query)
                db.commit()
                return {
                    "message": f"Project with key {project_key} deleted successfully"
                }
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error deleting project, please check your inputs",
                )
        case "admin":
            if not project_exists_key(project_key, db):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project with key {project_key} does not exist",
                )
            try:
                query = (
                    delete(table_models_required.Projects)
                    .where(table_models_required.Projects.company_id == user.company_id)
                    .where(table_models_required.Projects.project_key == project_key)
                )
                db.execute(query)
                db.commit()
                return {
                    "message": f"Project with key {project_key} deleted successfully"
                }
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error deleting project, please check your inputs",
                )
        case _:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authorized to delete projects as an admin",
            )
