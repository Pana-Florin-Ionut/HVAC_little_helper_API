from fastapi import Depends
from pytest import Session
from sqlalchemy import exists, literal, select, update

from app import schemas

from ..database import get_db

from .. import table_models_required


# def get_projects(company_id: int, db: Session = Depends(get_db)):
#     # query = select(table_models_required.Projects).where(
#     #     table_models_required.Projects.company_id == company_id
#     # )
#     projects: list[schemas.Project] = db.execute(
#         select(table_models_required.Projects).where(
#             table_models_required.Projects.company_id == company_id
#         )
#     ).fetchall()
#     # for project in projects:
#     #     print(type(project))
#     #     # project:
#     #     print(project)
#     # print(f"get_projects: {query}")
#     # projects: schemas.Project


#     # print(f"get_projects: {type(projects)}")
#     # print(projects)
#     return projects

def get_all_company_projects(company_id: int, db: Session = Depends(get_db)):
    """
    Return all projects from a company
    It does not check for permissions
    """
    projects = db.scalars(
        select(table_models_required.Projects).where(
            table_models_required.Projects.company_id == company_id
        )
    ).all()
    return projects


def update_project_name(
    projects: list[schemas.Project], old_project_name: str, new_project_name: str
):
    print(projects)
    # list_projects_name: list[str] = []
    # print(old_project_name)
    # print(new_project_name)
    for project in projects:
        new_prj: str = project.project_name.replace(old_project_name, new_project_name)
        project.project_name = new_prj
        # print(f"new_prj: {new_prj}")
    # print(f"Replaced projects: {list_projects_name}")
    return projects


def update_projects(
    company_id: int,
    old_company_key: str,
    new_company_key: str,
    db: Session = Depends(get_db),
):
    projects = get_all_company_projects(company_id, db)
    updated_projects = update_project_name(projects, old_company_key, new_company_key)
    for id, project in enumerate(projects):
        # print(f"id: {id}")
        # print(f"project: {project.project_name}")
        # print(f"updated_projects: {updated_projects[id].project_name}")
        query = (
            update(table_models_required.Projects)
            .where(table_models_required.Projects.id == project.id)
            .values(project_name=updated_projects[id].project_name)
        )
        db.execute(query)
        db.commit()


def rename_project_name(old_company_key: str, new_company_key: str, project_name: str):
    """
    Project name is made from company_key and project name
    ex: for company with key TS1 project with the name Project_one will be TS1_Project_one

    """
    return new_company_key + project_name.removeprefix(old_company_key)



# def update_products(
#     old_company_key: str, new_company_key: str, db: Session = Depends(get_db)
# ):
#     query = (
#         update(table_models_required.Products)
#         .where(table_models_required.Products.company_key == old_company_key)
#         .values(company_key=new_company_key)
#     )
#     db.execute(query)
#     db.commit()

# get all the projects for a company as a list of schema.Project
