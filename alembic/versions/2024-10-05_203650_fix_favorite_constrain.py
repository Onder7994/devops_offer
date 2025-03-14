"""Fix favorite constrain

Revision ID: 403e5f4df84e
Revises: 68d533512e88
Create Date: 2024-10-05 20:36:50.282700

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '403e5f4df84e'
down_revision: Union[str, None] = '68d533512e88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_favorites_question_id', 'favorites', type_='unique')
    op.create_unique_constraint('_user_question_uc', 'favorites', ['user_id', 'question_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_user_question_uc', 'favorites', type_='unique')
    op.create_unique_constraint('uq_favorites_question_id', 'favorites', ['question_id'])
    # ### end Alembic commands ###
