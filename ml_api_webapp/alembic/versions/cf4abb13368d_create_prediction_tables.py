from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "cf4abb13368d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    op.create_table("boosting_model_predictions",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("user_id", sa.String(length=36), nullable=False),
                    sa.Column("datetime_captured",
                              sa.DateTime(timezone=True),
                              server_default=sa.text("now()"),
                              nullable=True),
                    sa.Column("model_version", sa.String(length=36), nullable=False),
                    sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column("outputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.PrimaryKeyConstraint("id"))

    op.create_index(op.f("ix_boosting_model_predictions_datetime_captured"),
                    "boosting_model_predictions",
                    ["datetime_captured"],
                    unique=False)

    op.create_table("bagging_model_predictions",
                    sa.Column("id", sa.Integer(), nullable=False),
                    sa.Column("user_id", sa.String(length=36), nullable=False),
                    sa.Column("datetime_captured",
                              sa.DateTime(timezone=True),
                              server_default=sa.text("now()"),
                              nullable=True),
                    sa.Column("model_version", sa.String(length=36), nullable=False),
                    sa.Column("inputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column("outputs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.PrimaryKeyConstraint("id"))

    op.create_index(op.f("ix_bagging_model_predictions_datetime_captured"),
                    "bagging_model_predictions",
                    ["datetime_captured"],
                    unique=False)

    op.create_table('user_info',
                    sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
                    sa.Column('user_id', sa.String(length=36), nullable=False),
                    sa.Column('username', sa.String(length=50), nullable=False),
                    sa.Column('email', sa.String(length=120), nullable=False),
                    sa.Column('password', sa.String(length=255), nullable=False),
                    sa.Column('datetime_captured',
                              sa.DateTime(timezone=True),
                              server_default=sa.text('now()'),
                              nullable=True),
                    sa.PrimaryKeyConstraint("id"))


    op.create_index(op.f('ix_user_info_datetime_captured'),
                    'user_info',
                    ['datetime_captured'],
                    unique=False)



def downgrade():

    op.drop_index(op.f("ix_bagging_model_predictions_datetime_captured"),
                  table_name="bagging_model_predictions")
    op.drop_table("bagging_model_predictions")

    op.drop_index(op.f("ix_boosting_model_predictions_datetime_captured"),
                  table_name="boosting_model_predictions")
    op.drop_table("boosting_model_predictions")

    op.drop_index(op.f('ix_user_info_datetime_captured'),
                  table_name='user_info')
    op.drop_table('user_info')