from pydantic import BaseModel, Field, ConfigDict


class RepairCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    dealership_id: str = Field(min_length=1, max_length=100)
    repair_order_id: str = Field(min_length=1, max_length=100)
    vehicle_vin: str = Field(min_length=17, max_length=17)
    symptom: str = Field(min_length=1)
    diagnosis: str | None = None
    fix: str | None = None
    outcome: str | None = None


class RepairResponse(RepairCreate):
    id: str
    status: str
