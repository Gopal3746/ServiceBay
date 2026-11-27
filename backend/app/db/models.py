from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Repair(Base):
    __tablename__ = "repairs"

    __table_args__ = (
        UniqueConstraint(
            "dealership_id",
            "repair_order_id",
            name="uq_dealership_repair_order",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    dealership_id: Mapped[str] = mapped_column(String(100), nullable=False)
    repair_order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_vin: Mapped[str] = mapped_column(String(17), nullable=False)

    symptom: Mapped[str] = mapped_column(Text, nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    fix: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        String(30),
        default="received",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
