-- SQL script to create captive_portal_appliancetoken table
-- Execute this in PostgreSQL to resolve the missing table error

CREATE TABLE IF NOT EXISTS captive_portal_appliancetoken (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    appliance_id VARCHAR(100) UNIQUE NOT NULL,
    appliance_name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE,
    ip_address INET
);

-- Create indexes for better performance
CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_token_unique 
    ON captive_portal_appliancetoken(token);
CREATE UNIQUE INDEX IF NOT EXISTS captive_portal_appliancetoken_appliance_id_unique 
    ON captive_portal_appliancetoken(appliance_id);
CREATE INDEX IF NOT EXISTS captive_portal_appliancetoken_is_active_idx 
    ON captive_portal_appliancetoken(is_active);
CREATE INDEX IF NOT EXISTS captive_portal_appliancetoken_created_at_idx 
    ON captive_portal_appliancetoken(created_at);

-- Insert test tokens from JSON data
INSERT INTO captive_portal_appliancetoken (token, appliance_id, appliance_name, description, is_active, created_at)
VALUES 
    ('test-token-123456789', 'TEST-APPLIANCE', 'Appliance de Teste', 'Token de teste para desenvolvimento', TRUE, NOW()),
    ('f8e7d6c5b4a3928170695e4c3d2b1a0f', 'APPLIANCE-001', 'Appliance POPPFIRE 001', 'Token para appliance de produção 001', TRUE, NOW()),
    ('1234567890abcdef1234567890abcdef', 'APPLIANCE-DEV', 'Appliance de Desenvolvimento', 'Token para desenvolvimento e testes', TRUE, NOW())
ON CONFLICT (token) DO NOTHING;

-- Update last_used for the production token
UPDATE captive_portal_appliancetoken 
SET last_used = '2025-08-09 08:59:23.593932'::timestamp 
WHERE token = 'f8e7d6c5b4a3928170695e4c3d2b1a0f';

-- Mark migration as applied in django_migrations table
INSERT INTO django_migrations (app, name, applied) 
VALUES ('captive_portal', '0004_appliancetoken', NOW()) 
ON CONFLICT (app, name) DO NOTHING;

-- Verify table creation
SELECT 'Table created successfully. Total tokens: ' || COUNT(*) AS result 
FROM captive_portal_appliancetoken;
