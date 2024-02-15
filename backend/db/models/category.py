from sqlalchemy import (VARCHAR, BigInteger, Column, DateTime, ForeignKey,
                        Index, String, func)
from sqlalchemy.orm import relationship

from db.base import Base


class Category(Base):
    id = Column(BigInteger, primary_key=True, doc="Unique Category id")
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    title = Column(String, doc="Category title", nullable=False)
    description = Column(String, doc="Category description")
    type = Column(VARCHAR, nullable=False, doc="Category type")
    created_at = Column(
        DateTime(timezone=False),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        doc="Created at",
    )
    transaction = relationship("Transaction", back_populates="category", lazy="joined")
    user = relationship("User", back_populates="category", lazy="joined")

    __table_args__ = (
        Index("ix_category_title_btree", title, postgresql_using="btree"),
        Index("ix_category_description_btree", description, postgresql_using="btree"),
    )
