CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS symptom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    symptoms TEXT[] NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    urgency_level INT CHECK (urgency_level BETWEEN 1 AND 5),
    icd10_codes TEXT[],
    district TEXT,
    is_anonymous BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS facilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('hospital', 'pharmacy', 'blood_bank', 'aed')),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address TEXT,
    osm_id TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS icd10_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT,
    chapter TEXT
);

CREATE TABLE IF NOT EXISTS drug_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drug_a TEXT NOT NULL,
    drug_b TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('mild', 'moderate', 'severe')),
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS outbreak_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    source TEXT CHECK (source IN ('who_rss', 'dbscan', 'prophet')),
    title TEXT NOT NULL,
    description TEXT,
    latitude FLOAT,
    longitude FLOAT,
    district TEXT,
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    raw_data JSONB
);

CREATE INDEX IF NOT EXISTS idx_symptom_reports_symptoms_gin ON symptom_reports USING GIN (symptoms);
CREATE INDEX IF NOT EXISTS idx_facilities_lat_lng ON facilities (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_symptom_reports_created_at ON symptom_reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_outbreak_alerts_created_at ON outbreak_alerts (created_at DESC);

ALTER PUBLICATION supabase_realtime ADD TABLE symptom_reports;
