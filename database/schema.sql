-- NetGuard AI: PostgreSQL schema for a new database
-- Derived from the project's PostgreSQL schema-only export (2026-11-11).
-- Compatible with PostgreSQL 17+; contains no user data or credentials.
-- Intended for first-time initialization of an empty database.

BEGIN;

CREATE TABLE public.raw_network_traffic (
    id BIGSERIAL PRIMARY KEY,
    source_ip text,
    destination_ip text,
    protocol text,
    packets text,
    duration text,
    ingested_at timestamptz DEFAULT CURRENT_TIMESTAMP,
    source_key text
);

CREATE UNIQUE INDEX ux_raw_network_traffic_source_key
    ON public.raw_network_traffic (source_key);

CREATE TABLE public.processed_network_traffic (
    raw_id bigint PRIMARY KEY
        REFERENCES public.raw_network_traffic(id),
    source_ip text,
    destination_ip text,
    protocol text,
    packets integer,
    duration numeric,
    packets_per_second numeric,
    processed_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.ai_prediction_history (
    id BIGSERIAL PRIMARY KEY,
    prediction varchar(10) NOT NULL,
    ddos_probability_percent double precision NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    features jsonb,
    CONSTRAINT ai_prediction_history_ddos_probability_percent_check
        CHECK (ddos_probability_percent >= 0 AND ddos_probability_percent <= 100),
    CONSTRAINT ai_prediction_history_prediction_check
        CHECK (prediction IN ('BENIGN', 'DDoS'))
);

CREATE TABLE public.batch_analyses (
    id BIGSERIAL PRIMARY KEY,
    filename text NOT NULL,
    total_analyzed integer NOT NULL,
    benign_count integer NOT NULL,
    ddos_count integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT batch_analyses_benign_count_check CHECK (benign_count >= 0),
    CONSTRAINT batch_analyses_ddos_count_check CHECK (ddos_count >= 0),
    CONSTRAINT batch_analyses_total_analyzed_check CHECK (total_analyzed > 0),
    CONSTRAINT valid_batch_counts CHECK (benign_count + ddos_count = total_analyzed)
);

CREATE TABLE public.batch_prediction_results (
    id BIGSERIAL PRIMARY KEY,
    batch_id bigint NOT NULL
        REFERENCES public.batch_analyses(id) ON DELETE CASCADE,
    row_number integer NOT NULL,
    prediction text NOT NULL,
    ddos_probability_percent double precision NOT NULL,
    CONSTRAINT batch_prediction_results_ddos_probability_percent_check
        CHECK (ddos_probability_percent >= 0 AND ddos_probability_percent <= 100),
    CONSTRAINT batch_prediction_results_prediction_check
        CHECK (prediction IN ('BENIGN', 'DDoS')),
    CONSTRAINT batch_prediction_results_row_number_check CHECK (row_number > 0),
    CONSTRAINT unique_batch_row UNIQUE (batch_id, row_number)
);

CREATE INDEX idx_batch_results_batch_id
    ON public.batch_prediction_results (batch_id);

CREATE TABLE public.security_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type varchar(50) NOT NULL DEFAULT 'DDoS',
    severity varchar(20) NOT NULL,
    status varchar(20) NOT NULL DEFAULT 'Active',
    description text NOT NULL,
    ddos_probability_percent double precision,
    source varchar(50) NOT NULL DEFAULT 'simulation',
    created_at timestamptz NOT NULL DEFAULT now(),
    resolved_at timestamptz,
    CONSTRAINT security_alerts_check CHECK (
        (status = 'Active' AND resolved_at IS NULL)
        OR (status = 'Resolved' AND resolved_at IS NOT NULL)
    ),
    CONSTRAINT security_alerts_ddos_probability_percent_check
        CHECK (ddos_probability_percent >= 0 AND ddos_probability_percent <= 100),
    CONSTRAINT security_alerts_severity_check
        CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    CONSTRAINT security_alerts_status_check
        CHECK (status IN ('Active', 'Resolved'))
);

CREATE INDEX idx_security_alerts_created_at
    ON public.security_alerts (created_at DESC);

CREATE INDEX idx_security_alerts_status
    ON public.security_alerts (status);

COMMIT;
