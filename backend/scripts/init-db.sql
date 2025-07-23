-- HandyWriterz Database Initialization Script
-- This script sets up the initial database schema and extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO handywriterz;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO handywriterz;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO handywriterz;

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Initial system check
SELECT 'Database initialized successfully' as status;