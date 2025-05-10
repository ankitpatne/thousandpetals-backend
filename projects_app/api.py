from ninja import Router
from .models import Project
from typing import List
from ninja.orm import create_schema
from pydantic import BaseModel

router = Router()

class ProjectSchema(BaseModel):
    title: str
    description: str
    start_date: str
    end_date: str
    is_ongoing: bool = False

    class Config:
        from_attributes = True

@router.get("/")
def list_projects(request):
    projects = Project.objects.all()
    return [
        {
            "id": project.id,  # type: ignore
            "title": project.title,
            "description": project.description,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "is_ongoing": project.is_ongoing
        }
        for project in projects
    ]

@router.post("/", response=ProjectSchema)
def create_project(request, project: ProjectSchema):
    project_obj = Project.objects.create(
        title=project.title,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        is_ongoing=project.is_ongoing
    )
    return project_obj