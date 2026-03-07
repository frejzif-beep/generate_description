from sqlalchemy import String, Text, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from src.db.database import Base
from datetime import datetime
from typing import Dict, Any


class GeneratedDescription(Base):
    __tablename__ = "generated_descriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    
    def __repr__(self):
        return f"<GeneratedDescription(id={self.id}, category={self.category})>"