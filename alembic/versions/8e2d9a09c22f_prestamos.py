"""prestamos

Revision ID: 8e2d9a09c22f
Revises: ee3bdba69f8a
Create Date: 2024-03-20 00:10:18.666661

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8e2d9a09c22f'
down_revision: Union[str, None] = 'ee3bdba69f8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prestamos',
                    sa.Column('id_prestamo', sa.Integer(), nullable=False),
                    sa.Column('fecha', sa.Date(),
                              server_default=sa.text('(CURRENT_DATE)'),
                              nullable=True),
                    sa.Column('fecha_inicio', sa.Date(), nullable=True),
                    sa.Column('monto', sa.Float(), nullable=True),
                    sa.Column('monto_quincenal', sa.Float(), nullable=True),
                    sa.Column('comentarios', sa.String(), nullable=True),
                    sa.Column('id_usuario', sa.Integer(), nullable=True),
                    sa.Column('id_empleado', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['id_empleado'],
                                            ['empleados.id_empleado'], ),
                    sa.ForeignKeyConstraint(['id_usuario'],
                                            ['users.id_user'], ),
                    sa.PrimaryKeyConstraint('id_prestamo')
                    )
    op.create_index(op.f('ix_prestamos_id_prestamo'), 'prestamos',
                    ['id_prestamo'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_prestamos_id_prestamo'), table_name='prestamos')
    op.drop_table('prestamos')
    # ### end Alembic commands ###
