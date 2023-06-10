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

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

# company_key is the company key


@router.get("", status_code=status.HTTP_200_OK, response_model=list[schemas.Project])
def get_projects(
    user: schemas.UserOut = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    company_key: str = "",
    company_id_requested: int = 0,
):
    match user.role:
        case "application_administrator":
            try:
                projects = db.execute(
                    select(table_models_required.Projects)
                    .where(table_models_required.Projects.project_name.icontains(company_key))
                    .where(table_models_required.Projects.company_id == company_id_requested)
                ).fetchall()
                print(projects)
                return projects
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Company with key  does not exist",
                )


@router.post("/")
def create_project():
    return {"message": "create project"}
