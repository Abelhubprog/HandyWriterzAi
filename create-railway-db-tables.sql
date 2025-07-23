-- Railway PostgreSQL Database Schema
-- Run this after adding PostgreSQL to your Railway project

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- User memories table (replaces Supabase user_memories)
CREATE TABLE IF NOT EXISTS user_memories (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    fingerprint JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster user lookups
CREATE INDEX IF NOT EXISTS idx_user_memories_user_id ON user_memories(user_id);

-- Tutor feedback table (for fine-tuning pipeline)
CREATE TABLE IF NOT EXISTS tutor_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    original_text TEXT NOT NULL,
    comment TEXT NOT NULL,
    rewritten_text TEXT,
    feedback_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for date-based queries
CREATE INDEX IF NOT EXISTS idx_tutor_feedback_created_at ON tutor_feedback(created_at);
CREATE INDEX IF NOT EXISTS idx_tutor_feedback_user_id ON tutor_feedback(user_id);

-- Update trigger for user_memories
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_memories_updated_at 
    BEFORE UPDATE ON user_memories 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tutor_feedback_updated_at 
    BEFORE UPDATE ON tutor_feedback 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Verify tables were created
\d user_memories;
\d tutor_feedback;

-- Show available extensions
SELECT * FROM pg_extension WHERE extname = 'vector';

COMMENT ON TABLE user_memories IS 'Stores user writing fingerprints and preferences (replaces Supabase)';
COMMENT ON TABLE tutor_feedback IS 'Stores tutor feedback for fine-tuning pipeline';

-- Example queries
-- INSERT INTO user_memories (user_id, fingerprint) VALUES ('test_user', '{"style": "academic", "tone": "formal"}');
-- SELECT * FROM user_memories WHERE user_id = 'test_user';