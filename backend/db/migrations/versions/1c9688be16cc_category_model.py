"""category model

Revision ID: 1c9688be16cc
Revises: 615e7cb6d88a
Create Date: 2024-02-13 18:02:17.390693

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1c9688be16cc"
down_revision: Union[str, None] = "615e7cb6d88a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("type", sa.VARCHAR(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_category_description_btree",
        "category",
        ["description"],
        unique=False,
        postgresql_using="btree",
    )
    op.create_index(
        "ix_category_title_btree",
        "category",
        ["title"],
        unique=False,
        postgresql_using="btree",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "ix_category_title_btree", table_name="category", postgresql_using="btree"
    )
    op.drop_index(
        "ix_category_description_btree", table_name="category", postgresql_using="btree"
    )
    op.drop_table("category")
    # ### end Alembic commands ###