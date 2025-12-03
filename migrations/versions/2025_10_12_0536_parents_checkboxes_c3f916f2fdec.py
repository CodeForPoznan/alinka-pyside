"""parents_checkboxes

Revision ID: c3f916f2fdec
Revises: 4661708a4685
Create Date: 2025-10-12 05:36:35.547597

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3f916f2fdec"
down_revision: Union[str, None] = "4661708a4685"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("decision", "address_child_checkbox", new_column_name="is_first_parent_address_different")
    op.alter_column("decision", "address_first_parent_checkbox", new_column_name="is_second_parent_address_different")
    op.execute(
        """
        UPDATE decision
        SET is_first_parent_address_different = NOT is_first_parent_address_different
    """
    )
    op.execute(
        """
        UPDATE decision
        SET is_second_parent_address_different = NOT is_second_parent_address_different
        WHERE second_parent_full_name IS NOT NULL
    """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE decision
        SET is_first_parent_address_different = NOT is_first_parent_address_different
    """
    )
    op.execute(
        """
        UPDATE decision
        SET is_second_parent_address_different = NOT is_second_parent_address_different
        WHERE second_parent_full_name IS NOT NULL
    """
    )
    op.alter_column("decision", "is_first_parent_address_different", new_column_name="address_child_checkbox")
    op.alter_column("decision", "is_second_parent_address_different", new_column_name="address_first_parent_checkbox")
