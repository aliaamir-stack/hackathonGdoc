-- Supabase Schema for PULSE Hackathon
-- Run this in the Supabase SQL Editor

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Symptom Reports Table (Needs Realtime Enabled)
CREATE TABLE IF NOT EXISTS symptom_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    symptom_type TEXT NOT NULL,
    urgency INTEGER CHECK (urgency BETWEEN 1 AND 5),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Note: To enable Realtime on symptom_reports, go to Supabase Dashboard -> Database -> Replication and enable it for this table.

-- 3. Facilities Table
CREATE TABLE IF NOT EXISTS facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    type TEXT NOT NULL, -- 'hospital', 'pharmacy', 'blood_bank', 'defibrillator'
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (name, lat, lng)
);

-- 4. ICD-10 Codes Table
CREATE TABLE IF NOT EXISTS icd10_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT,
    chapter TEXT
);

-- 5. Drug Interactions Table
CREATE TABLE IF NOT EXISTS drug_interactions (
    id SERIAL PRIMARY KEY,
    drug_a TEXT NOT NULL,
    drug_b TEXT NOT NULL,
    description TEXT,
    UNIQUE (drug_a, drug_b)
);

-- 6. Outbreak Alerts (WHO RSS) Table
CREATE TABLE IF NOT EXISTS outbreak_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    link TEXT UNIQUE,
    pub_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
