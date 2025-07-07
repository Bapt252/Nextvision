-- === NEXTVISION DATABASE INITIALIZATION ===
-- Production database setup with optimizations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create application user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'nextvision_user') THEN
        CREATE ROLE nextvision_user LOGIN PASSWORD 'nextvision_password';
    END IF;
END
$$;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE nextvision_prod TO nextvision_user;
GRANT USAGE ON SCHEMA public TO nextvision_user;
GRANT CREATE ON SCHEMA public TO nextvision_user;

-- Create core tables (if they don't exist)
CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    skills JSONB,
    experience_years INTEGER,
    education TEXT,
    current_role TEXT,
    location JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    description TEXT,
    requirements JSONB,
    salary_range JSONB,
    location JSONB,
    remote_policy VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS matching_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id),
    job_id UUID REFERENCES jobs(id),
    matching_score DECIMAL(5,3),
    component_scores JSONB,
    weights_used JSONB,
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,3),
    labels JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    error_type VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    context JSONB,
    severity VARCHAR(20),
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_location ON candidates USING GIN(location);
CREATE INDEX IF NOT EXISTS idx_candidates_skills ON candidates USING GIN(skills);
CREATE INDEX IF NOT EXISTS idx_candidates_created_at ON candidates(created_at);

CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs USING GIN(location);
CREATE INDEX IF NOT EXISTS idx_jobs_requirements ON jobs USING GIN(requirements);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_matching_candidate_job ON matching_results(candidate_id, job_id);
CREATE INDEX IF NOT EXISTS idx_matching_score ON matching_results(matching_score DESC);
CREATE INDEX IF NOT EXISTS idx_matching_created_at ON matching_results(created_at);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_name_time ON performance_metrics(metric_name, recorded_at);
CREATE INDEX IF NOT EXISTS idx_error_logs_type_time ON error_logs(error_type, occurred_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_candidates_updated_at BEFORE UPDATE ON candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nextvision_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO nextvision_user;

-- Performance optimizations
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- Create sample data for testing (comment out in production)
-- INSERT INTO candidates (first_name, last_name, email, skills, experience_years, location) VALUES
-- ('John', 'Doe', 'john.doe@example.com', '{"skills": ["Python", "FastAPI", "PostgreSQL"]}', 5, '{"city": "Paris", "country": "France"}'),
-- ('Jane', 'Smith', 'jane.smith@example.com', '{"skills": ["JavaScript", "React", "Node.js"]}', 3, '{"city": "Lyon", "country": "France"}');

COMMIT;
