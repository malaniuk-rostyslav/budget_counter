from sqlalchemy import (DECIMAL, VARCHAR, BigInteger, Column, Date, DateTime,
                        ForeignKey, Index, String, func)
from sqlalchemy.orm import relationship

from db.base import Base
from db.models import constants


class Transaction(Base):
    id = Column(BigInteger, primary_key=True, doc="Unique id")
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    category_id = Column(
        BigInteger,
        ForeignKey("category.id", ondelete="CASCADE"),
        nullable=False,
        doc="Category id",
    )
    amount = Column(DECIMAL, nullable=False, doc="Record amount")
    currency = Column(
        VARCHAR,
        nullable=False,
        default=constants.CurrencyEnum.UAH.value,
        doc="Transaction currency",
    )
    date = Column(Date, nullable=False, doc="Record date")
    note = Column(String, doc="Record note")
    created_at = Column(
        DateTime(timezone=False),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        doc="Created at",
    )
    category = relationship("Category", back_populates="transaction", lazy="noload")
    user = relationship("User", back_populates="transaction", lazy="joined")

    __table_args__ = (
        Index("ix_transaction_amount_btree", amount, postgresql_using="btree"),
        Index("ix_transaction_currency_btree", currency, postgresql_using="btree"),
        Index("ix_transaction_date_btree", date, postgresql_using="btree"),
        Index("ix_transaction_note_btree", note, postgresql_using="btree"),
    )
