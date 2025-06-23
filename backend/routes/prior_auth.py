from typing import List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from schemas import (
    PriorAuthorizationCreate,
    PriorAuthorizationResponse,
    PriorAuthorizationUpdate,
)
from services.prior_auth_service import PriorAuthService
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("", response_model=List[PriorAuthorizationResponse])
def get_prior_authorizations(db: Session = Depends(get_db)):
    """Get all prior authorizations"""
    return PriorAuthService.get_all(db)


@router.get("/{auth_id}", response_model=PriorAuthorizationResponse)
def get_prior_authorization(auth_id: str, db: Session = Depends(get_db)):
    """Get a single prior authorization by ID"""
    prior_auth = PriorAuthService.get_by_id(db, auth_id)
    if not prior_auth:
        raise HTTPException(status_code=404, detail="Prior authorization not found")
    return prior_auth


@router.post("", response_model=PriorAuthorizationResponse)
def create_prior_authorization(
    prior_auth: PriorAuthorizationCreate, db: Session = Depends(get_db)
):
    """Create new prior authorization"""
    try:
        return PriorAuthService.create(db, prior_auth)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{auth_id}", response_model=PriorAuthorizationResponse)
def update_prior_authorization(
    auth_id: str,
    prior_auth_update: PriorAuthorizationUpdate,
    db: Session = Depends(get_db),
):
    """Update existing prior authorization"""
    prior_auth = PriorAuthService.update(db, auth_id, prior_auth_update)
    if not prior_auth:
        raise HTTPException(status_code=404, detail="Prior authorization not found")
    return prior_auth


@router.delete("/{auth_id}")
def delete_prior_authorization(auth_id: str, db: Session = Depends(get_db)):
    """Delete prior authorization"""
    if not PriorAuthService.delete(db, auth_id):
        raise HTTPException(status_code=404, detail="Prior authorization not found")
    return {"message": "Prior authorization deleted successfully"}
