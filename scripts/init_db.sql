-- Initialization script for ACAT System PostgreSQL Database
-- Creates the database and enables PostGIS extension

-- Create database (if not exists)
SELECT 'CREATE DATABASE acat_system_dev' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'acat_system_dev')\gexec

-- Connect to the database and enable PostGIS
\c acat_system_dev

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Grant permissions to user
GRANT ALL PRIVILEGES ON DATABASE acat_system_dev TO acat_user;
