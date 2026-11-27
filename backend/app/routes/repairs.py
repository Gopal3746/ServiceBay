from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Repair
from app.models.repair import RepairCreate, RepairResponse


router = APIRouter(prefix="/repairs", tags=["repairs"])


@router.post(
    "",
    response_model=RepairResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repair(
    payload: RepairCreate,
    db: Session = Depends(get_db),
):
    repair = Repair(**payload.model_dump())

    db.add(repair)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Repair order already exists for this dealership",
        )

    db.refresh(repair)
    return repair


@router.get("/{repair_id}", response_model=RepairResponse)
def get_repair(
    repair_id: str,
    db: Session = Depends(get_db),
):
    repair = db.get(Repair, repair_id)

    if repair is None:
        raise HTTPException(
            status_code=404,
            detail="Repair not found",
        )

    return repair
