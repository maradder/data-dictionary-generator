"""add_performance_indexes

Revision ID: 025d9be916ff
Revises: 0cf0e9fac7fa
Create Date: 2025-11-12 16:40:55.490460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '025d9be916ff'
down_revision: Union[str, None] = '0cf0e9fac7fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for foreign keys and common queries."""
    # Index for versions lookups by dictionary
    op.create_index(
        'idx_versions_dictionary_id',
        'versions',
        ['dictionary_id'],
        unique=False
    )

    # Index for fields lookups by version
    op.create_index(
        'idx_fields_version_id',
        'fields',
        ['version_id'],
        unique=False
    )

    # Index for field path searches
    op.create_index(
        'idx_fields_field_path',
        'fields',
        ['field_path'],
        unique=False
    )

    # Index for annotations lookups by field
    op.create_index(
        'idx_annotations_field_id',
        'annotations',
        ['field_id'],
        unique=False
    )

    # Index for PII field queries
    op.create_index(
        'idx_fields_is_pii',
        'fields',
        ['is_pii'],
        unique=False
    )

    # Index for data type filtering
    op.create_index(
        'idx_fields_data_type',
        'fields',
        ['data_type'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('idx_fields_data_type', table_name='fields')
    op.drop_index('idx_fields_is_pii', table_name='fields')
    op.drop_index('idx_annotations_field_id', table_name='annotations')
    op.drop_index('idx_fields_field_path', table_name='fields')
    op.drop_index('idx_fields_version_id', table_name='fields')
    op.drop_index('idx_versions_dictionary_id', table_name='versions')
