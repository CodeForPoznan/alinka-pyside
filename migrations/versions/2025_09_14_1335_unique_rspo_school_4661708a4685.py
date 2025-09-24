"""unique_rspo_school

Revision ID: 4661708a4685
Revises: 8efed76c37b5
Create Date: 2025-09-14 13:35:19.176507

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4661708a4685"
down_revision: Union[str, None] = "8efed76c37b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM school
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM school
                WHERE rspo_id IS NOT NULL
                GROUP BY rspo_id
            )
            AND rspo_id IS NOT NULL
            AND rspo_id IN (
                SELECT rspo_id FROM school
                WHERE rspo_id IS NOT NULL
                GROUP BY rspo_id
                HAVING COUNT(*) > 1
            )
            """
        )
    )
    with op.batch_alter_table("school", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_school_rspo_id", ["rspo_id"])


def downgrade() -> None:
    with op.batch_alter_table("school", schema=None) as batch_op:
        batch_op.drop_constraint("uq_school_rspo_id", type_="unique")
