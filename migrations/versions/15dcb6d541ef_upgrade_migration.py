"""Upgrade Migration

Revision ID: 15dcb6d541ef
Revises: 44b4c3f37968
Create Date: 2022-07-18 01:25:08.066491

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15dcb6d541ef'
down_revision = '44b4c3f37968'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gender', sa.String(length=5), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('biography', sa.Text(), nullable=False),
    sa.Column('website', sa.String(length=60), nullable=True),
    sa.Column('image_file', sa.String(length=20), nullable=True),
    sa.Column('date_joined', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_slug'), 'user', ['slug'], unique=True)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('post_cover', sa.String(length=20), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(length=200), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_index(op.f('ix_post_slug'), 'post', ['slug'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_post_slug'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_user_slug'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
