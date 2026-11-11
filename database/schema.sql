
-- ============================================
-- NetGuard AI - Database Schema
-- Security Alerts Table
-- ============================================

CREATE TABLE IF NOT EXISTS public.security_alerts (
    id BIGSERIAL PRIMARY KEY,

    alert_type VARCHAR(50) NOT NULL DEFAULT 'DDoS',

    severity VARCHAR(20) NOT NULL
        CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),

    status VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (status IN ('Active', 'Resolved')),

    description TEXT NOT NULL,

    ddos_probability_percent DOUBLE PRECISION
        CHECK (
            ddos_probability_percent >= 0
            AND ddos_probability_percent <= 100
        ),

    source VARCHAR(50) NOT NULL DEFAULT 'simulation',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    resolved_at TIMESTAMPTZ,

    CHECK (
        (status = 'Active' AND resolved_at IS NULL)
        OR
        (status = 'Resolved' AND resolved_at IS NOT NULL)
    )
);

-- Index for filtering alerts by status
CREATE INDEX IF NOT EXISTS idx_security_alerts_status
ON public.security_alerts (status);

-- Index for sorting alerts by creation time
CREATE INDEX IF NOT EXISTS idx_security_alerts_created_at
ON public.security_alerts (created_at DESC);
