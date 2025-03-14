"""Fix relationship

Revision ID: 8465f5cbd55e
Revises: 7fdb3277dbf3
Create Date: 2024-09-26 19:47:05.469131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8465f5cbd55e'
down_revision: Union[str, None] = '7fdb3277dbf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_answers_question_id_questions', 'answers', type_='foreignkey')
    op.create_foreign_key(op.f('fk_answers_question_id_questions'), 'answers', 'questions', ['question_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_answers_question_id_questions'), 'answers', type_='foreignkey')
    op.create_foreign_key('fk_answers_question_id_questions', 'answers', 'questions', ['question_id'], ['id'])
    # ### end Alembic commands ###
