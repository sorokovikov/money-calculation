"""add status and last seen

Revision ID: 444f602d771f
Revises: 781a18569f1b
Create Date: 2020-02-09 17:39:50.312982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '444f602d771f'
down_revision = '781a18569f1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('status', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'status')
    op.drop_column('user', 'last_seen')
    # ### end Alembic commands ###
