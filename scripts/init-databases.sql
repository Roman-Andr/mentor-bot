-- Multi-database initialization for DB-per-service architecture
-- Creates 8 separate databases, one per service

-- Auth Service Database
CREATE DATABASE auth_db;
CREATE DATABASE checklists_db;
CREATE DATABASE knowledge_db;
CREATE DATABASE notification_db;
CREATE DATABASE escalation_db;
CREATE DATABASE meeting_db;
CREATE DATABASE feedback_db;
CREATE DATABASE telegram_db;