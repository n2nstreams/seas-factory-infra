-- Description: Create a table to store user feature embeddings for personalization.
-- This table will be used by the PersonalizationAgent to store and query user embeddings.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE user_feature_embeddings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    feature_name VARCHAR(255) NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON user_feature_embeddings USING hnsw (embedding vector_l2_ops);

COMMENT ON TABLE user_feature_embeddings IS 'Stores user feature embeddings for personalization.';
COMMENT ON COLUMN user_feature_embeddings.user_id IS 'The ID of the user.';
COMMENT ON COLUMN user_feature_embeddings.feature_name IS 'The name of the feature being embedded (e.g., "preferred_stack", "project_description").';
COMMENT ON COLUMN user_feature_embeddings.embedding IS 'The 384-dimensional feature embedding from sentence-transformers/all-MiniLM-L6-v2.'; 