-- SaaS Factory Database Initialization
-- This script sets up the complete database schema for multi-tenant SaaS factory

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Run tenant model migration
\i /docker-entrypoint-initdb.d/migrations/001_create_tenant_model.sql 