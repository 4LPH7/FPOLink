-- FPOLink TN Database Initialization
-- This runs automatically on first PostgreSQL container start

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Ensure the database is ready for UTF-8 Tamil text
ALTER DATABASE fpolink SET client_encoding TO 'UTF8';
