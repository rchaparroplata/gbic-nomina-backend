"""salarios

Revision ID: 83b07dc3f704
Revises: 8e2d9a09c22f
Create Date: 2024-03-23 20:13:37.549126

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '83b07dc3f704'
down_revision: Union[str, None] = '8e2d9a09c22f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('salarios',
                    sa.Column('id_salario', sa.Integer(), nullable=False),
                    sa.Column('fecha',
                              sa.Date(),
                              server_default=sa.text('(CURRENT_DATE)'),
                              nullable=True),
                    sa.Column('fecha_valido', sa.Date(), nullable=True),
                    sa.Column('monto', sa.Float(), nullable=True),
                    sa.Column('id_empleado', sa.Integer(), nullable=True),
                    sa.Column('id_usuario', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['id_empleado'],
                                            ['empleados.id_empleado'], ),
                    sa.ForeignKeyConstraint(['id_usuario'],
                                            ['users.id_user'], ),
                    sa.PrimaryKeyConstraint('id_salario')
                    )
    op.create_index(op.f('ix_salarios_id_salario'),
                    'salarios',
                    ['id_salario'],
                    unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_salarios_id_salario'), table_name='salarios')
    op.drop_table('salarios')
    # ### end Alembic commands ###
