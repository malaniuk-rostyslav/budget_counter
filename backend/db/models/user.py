from sqlalchemy import (VARCHAR, BigInteger, Boolean, Column, Date, DateTime,
                        ForeignKey, Index, String, event, func, insert)
from sqlalchemy.orm import relationship

from db.base import Base
from db.models import constants


class User(Base):
    id = Column(BigInteger, primary_key=True, doc="Unique id")
    email = Column(String, doc="Unique email address", unique=True)
    hashed_password = Column(String, doc="Hashed password")
    is_superuser = Column(
        Boolean(), default=False, nullable=False, doc="Super user identifier"
    )
    birthday = Column(Date, doc="Birthday of user")
    created_at = Column(
        DateTime(timezone=False),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        doc="Created at",
    )
    settings = relationship(
        "UserSettings",
        backref="user",
        lazy="joined",
        uselist=False,
    )

    __table_args__ = (
        Index("ix_user_email_btree", email, unique=True, postgresql_using="btree"),
        Index("ix_user_birthday_btree", birthday, postgresql_using="btree"),
    )


class UserSettings(Base):
    id = Column(BigInteger, primary_key=True, doc="Unique id")
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    notification_on = Column(
        Boolean(), default=True, nullable=False, doc="Is User notification status "
    )
    currency = Column(
        VARCHAR,
        nullable=False,
        default=constants.CurrencyEnum.UAH.value,
        doc="User currency",
    )
    created_at = Column(
        DateTime(timezone=False),
        default=func.now(),
        nullable=False,
        doc="Created at",
    )
    __table_args__ = (
        Index(
            "ix_user_settings_notification_on_btree",
            notification_on,
            postgresql_using="btree",
        ),
        Index("ix_user_settings_currency_btree", currency, postgresql_using="btree"),
    )


class Device(Base):
    id = Column(BigInteger, primary_key=True, doc="Unique id")
    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    last_login = Column(
        DateTime(timezone=False),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        doc="Created at",
    )
    fcm_token = Column(String, doc="Firebase Token")
    __table_args__ = (
        Index(
            "ix_device_user_id_btree",
            user_id,
            postgresql_using="btree",
        ),
        Index("ix_device_last_login_btree", last_login, postgresql_using="btree"),
    )


@event.listens_for(User, "after_insert")
def post_create_user_settings(mapper, connection, target):
    if target.id and not target.settings:
        st_slue = insert(UserSettings).values(user_id=target.id)
        connection.execute(st_slue)
