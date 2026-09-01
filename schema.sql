-- Legal & Civic Service Assistant — Database Schema Reference
-- Tables are auto-created by Flask-SQLAlchemy when app.py runs.
-- This file is just for reference / manual creation if needed.

CREATE DATABASE IF NOT EXISTS legal_civic_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE legal_civic_db;

-- Tables created automatically by SQLAlchemy:
--   users              (id, fullname, email, mobile, nic, password,
--                        preferred_language, role, created_at)
--   gov_services        (id, name, category, icon, description,
--                        official_link, status, created_at)
--   service_steps       (id, service_id, step_number, title, description)
--   required_documents  (id, service_id, document_name, is_mandatory)
--   chat_history         (id, user_id, question, response, language, created_at)
--   saved_guides         (id, user_id, service_id, saved_at)
--   official_links       (id, title, url, department, icon)

-- After running `python app.py` once (creates tables + admin user),
-- run `python seed_data.py` to populate sample services, steps, and documents.
