#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until psql -U "${POSTGRES_USER}" -d postgres -c '\q' 2>/dev/null; do
  sleep 1
done

echo "Creating databases for DB-per-service architecture..."

psql -U "${POSTGRES_USER}" -d postgres <<-EOSQL
  -- Drop existing databases if they exist (careful in production!)
  -- SELECT 'DROP DATABASE IF EXISTS ' || datname || ';' FROM pg_database WHERE datname IN (
  --   'auth_db', 'checklists_db', 'knowledge_db', 'notification_db',
  --   'escalation_db', 'meeting_db', 'feedback_db', 'telegram_db'
  -- );

  CREATE DATABASE auth_db;
  CREATE DATABASE checklists_db;
  CREATE DATABASE knowledge_db;
  CREATE DATABASE notification_db;
  CREATE DATABASE escalation_db;
  CREATE DATABASE meeting_db;
  CREATE DATABASE feedback_db;
  CREATE DATABASE telegram_db;
EOSQL

echo "Databases created successfully!"