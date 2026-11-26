from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.models.repair import RepairCreate, RepairResponse

router = APIRouter(prefix="/repairs", tags=["repairs"])

repairs: dict[str, RepairResponse] = {}
repair_keys: dict[tuple[str, str], str] = {}


@router.post(
    "",
    response_model=RepairResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_repair(payload: RepairCreate):
    key = (payload.dealership_id, payload.repair_order_id)

    if key in repair_keys:
        raise HTTPException(
            status_code=409,
            detail="Repair order already exists for this dealership",
        )

    repair = RepairResponse(
        **payload.model_dump(),
        id=str(uuid4()),
        status="received",
    )

    repairs[repair.id] = repair
    repair_keys[key] = repair.id

    return repair


@router.get("/{repair_id}", response_model=RepairResponse)
def get_repair(repair_id: str):
    repair = repairs.get(repair_id)

    if repair is None:
        raise HTTPException(
            status_code=404,
            detail="Repair not found",
        )

    return repair
