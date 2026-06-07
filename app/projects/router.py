from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.user import User
from app.projects.dependencies import require_project_member
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectResponse,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    project = Project(name=payload.name, description=payload.description, created_by=current_user.id)
    db.add(project)
    db.flush()

    membership = ProjectMember(user_id=current_user.id, project_id=project.id, role=ProjectRole.owner)
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Project]:
    return (
        db.query(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(ProjectMember.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_membership: Annotated[tuple[Project, ProjectMember], Depends(require_project_member())],
) -> Project:
    project, _ = project_membership
    return project


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: UUID,
    payload: ProjectMemberCreate,
    project_membership: Annotated[tuple[Project, ProjectMember], Depends(require_project_member(ProjectRole.admin))],
    db: Annotated[Session, Depends(get_db)],
) -> ProjectMemberResponse:
    project, _membership = project_membership

    if payload.role == ProjectRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign owner role")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member")

    member = ProjectMember(user_id=user.id, project_id=project.id, role=payload.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return ProjectMemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=user.email,
        role=member.role,
        created_at=member.created_at,
    )


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: UUID,
    user_id: UUID,
    project_membership: Annotated[tuple[Project, ProjectMember], Depends(require_project_member(ProjectRole.admin))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    project, membership = project_membership
    target = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == user_id)
        .first()
    )
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if target.role == ProjectRole.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove project owner")

    if membership.role == ProjectRole.admin and target.role == ProjectRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot remove other admins")

    db.delete(target)
    db.commit()
