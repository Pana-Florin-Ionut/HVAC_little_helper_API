from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

# co_key is the company key


@router.get("/{co_key}", status_code=status.HTTP_200_OK)
def get_projects(co_key: str | None = None):
    if co_key is None:
        return {"message": "get all projects"}

    return {"message": f"get projects - project key = {co_key}"}


@router.post("/")
def create_project():
    return {"message": "create project"}
