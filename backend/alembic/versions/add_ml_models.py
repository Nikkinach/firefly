"""Add ML models for NLP, predictions, and collaborative filtering

Revision ID: ml_features_001
Revises:
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ml_features_001'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Journal Analyses
    op.create_table(
        'journal_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('journal_entry_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(), nullable=True),
        sa.Column('sentiment_confidence', sa.Float(), nullable=True),
        sa.Column('primary_emotion', sa.String(), nullable=True),
        sa.Column('primary_emotion_score', sa.Float(), nullable=True),
        sa.Column('all_emotions', sa.JSON(), nullable=True),
        sa.Column('crisis_detected', sa.Boolean(), nullable=True, default=False),
        sa.Column('crisis_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('matched_keywords', sa.JSON(), nullable=True),
        sa.Column('requires_immediate_attention', sa.Boolean(), nullable=True, default=False),
        sa.Column('themes', sa.JSON(), nullable=True),
        sa.Column('text_length', sa.Integer(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_journal_analyses_id'), 'journal_analyses', ['id'], unique=False)

    # Mood Predictions
    op.create_table(
        'mood_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('prediction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('predicted_mood', sa.Float(), nullable=False),
        sa.Column('confidence_lower', sa.Float(), nullable=True),
        sa.Column('confidence_upper', sa.Float(), nullable=True),
        sa.Column('model_type', sa.String(), nullable=True),
        sa.Column('model_version', sa.String(), nullable=True),
        sa.Column('actual_mood', sa.Float(), nullable=True),
        sa.Column('prediction_error', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mood_predictions_id'), 'mood_predictions', ['id'], unique=False)

    # Seasonal Patterns
    op.create_table(
        'seasonal_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pattern_type', sa.String(), nullable=True),
        sa.Column('pattern_data', sa.JSON(), nullable=True),
        sa.Column('best_day', sa.String(), nullable=True),
        sa.Column('worst_day', sa.String(), nullable=True),
        sa.Column('weekly_p_value', sa.Float(), nullable=True),
        sa.Column('best_month', sa.String(), nullable=True),
        sa.Column('worst_month', sa.String(), nullable=True),
        sa.Column('dominant_cycles', sa.JSON(), nullable=True),
        sa.Column('data_span_days', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seasonal_patterns_id'), 'seasonal_patterns', ['id'], unique=False)

    # Correlation Analyses
    op.create_table(
        'correlation_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('analysis_type', sa.String(), nullable=True),
        sa.Column('correlation_data', sa.JSON(), nullable=True),
        sa.Column('primary_correlation', sa.Float(), nullable=True),
        sa.Column('primary_factor', sa.String(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('is_significant', sa.Boolean(), nullable=True),
        sa.Column('n_data_points', sa.Integer(), nullable=True),
        sa.Column('date_range_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_range_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_correlation_analyses_id'), 'correlation_analyses', ['id'], unique=False)

    # User Profiles (Anonymized)
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('features', sa.JSON(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=True),
        sa.Column('cluster_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('n_data_points', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_user_profiles_profile_id'), 'user_profiles', ['profile_id'], unique=True)

    # Intervention Effectiveness
    op.create_table(
        'intervention_effectiveness',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('intervention_id', sa.String(), nullable=False),
        sa.Column('effectiveness_score', sa.Float(), nullable=False),
        sa.Column('n_uses', sa.Integer(), default=1),
        sa.Column('mood_before', sa.Float(), nullable=True),
        sa.Column('mood_after', sa.Float(), nullable=True),
        sa.Column('mood_improvement', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['user_profiles.profile_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intervention_effectiveness_id'), 'intervention_effectiveness', ['id'], unique=False)

    # A/B Tests
    op.create_table(
        'ab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('variants', sa.JSON(), nullable=False),
        sa.Column('target_metric', sa.String(), nullable=False),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('winner', sa.String(), nullable=True),
        sa.Column('statistical_significance', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ab_tests_id'), 'ab_tests', ['id'], unique=False)
    op.create_index(op.f('ix_ab_tests_test_id'), 'ab_tests', ['test_id'], unique=True)

    # A/B Test Assignments
    op.create_table(
        'ab_test_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.String(), nullable=False),
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('variant_id', sa.String(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.test_id'], ),
        sa.ForeignKeyConstraint(['profile_id'], ['user_profiles.profile_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ab_test_assignments_id'), 'ab_test_assignments', ['id'], unique=False)

    # A/B Test Results
    op.create_table(
        'ab_test_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.String(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.test_id'], ),
        sa.ForeignKeyConstraint(['assignment_id'], ['ab_test_assignments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ab_test_results_id'), 'ab_test_results', ['id'], unique=False)

    # ML Model Versions
    op.create_table(
        'ml_model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('architecture', sa.JSON(), nullable=True),
        sa.Column('hyperparameters', sa.JSON(), nullable=True),
        sa.Column('training_data_size', sa.Integer(), nullable=True),
        sa.Column('training_loss', sa.Float(), nullable=True),
        sa.Column('validation_loss', sa.Float(), nullable=True),
        sa.Column('test_metrics', sa.JSON(), nullable=True),
        sa.Column('model_path', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ml_model_versions_id'), 'ml_model_versions', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ml_model_versions_id'), table_name='ml_model_versions')
    op.drop_table('ml_model_versions')

    op.drop_index(op.f('ix_ab_test_results_id'), table_name='ab_test_results')
    op.drop_table('ab_test_results')

    op.drop_index(op.f('ix_ab_test_assignments_id'), table_name='ab_test_assignments')
    op.drop_table('ab_test_assignments')

    op.drop_index(op.f('ix_ab_tests_test_id'), table_name='ab_tests')
    op.drop_index(op.f('ix_ab_tests_id'), table_name='ab_tests')
    op.drop_table('ab_tests')

    op.drop_index(op.f('ix_intervention_effectiveness_id'), table_name='intervention_effectiveness')
    op.drop_table('intervention_effectiveness')

    op.drop_index(op.f('ix_user_profiles_profile_id'), table_name='user_profiles')
    op.drop_index(op.f('ix_user_profiles_id'), table_name='user_profiles')
    op.drop_table('user_profiles')

    op.drop_index(op.f('ix_correlation_analyses_id'), table_name='correlation_analyses')
    op.drop_table('correlation_analyses')

    op.drop_index(op.f('ix_seasonal_patterns_id'), table_name='seasonal_patterns')
    op.drop_table('seasonal_patterns')

    op.drop_index(op.f('ix_mood_predictions_id'), table_name='mood_predictions')
    op.drop_table('mood_predictions')

    op.drop_index(op.f('ix_journal_analyses_id'), table_name='journal_analyses')
    op.drop_table('journal_analyses')
