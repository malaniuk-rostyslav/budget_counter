from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Index,
                        String, func)

from db.base import Base


class User(Base):
    id = Column(BigInteger, primary_key=True, doc="Unique id")
    email = Column(String, doc="Unique email address", unique=True)
    hashed_password = Column(String, doc="Hashed password")
    is_superuser = Column(
        Boolean(), default=False, nullable=False, doc="Super user identifier"
    )
    is_active = Column(
        Boolean(), default=False, nullable=False, doc="Active user identifier"
    )
    birthday = Column(Date, doc="Birthday of user")
    created_at = Column(
        DateTime(timezone=False),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        doc="Created at",
    )

    __table_args__ = (
        Index("ix_user_email_btree", email, unique=True, postgresql_using="btree"),
        Index("ix_user_birthday_btree", birthday, postgresql_using="btree"),
    )
