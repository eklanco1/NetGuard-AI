
-- NetGuard AI - Synthetic Demo Data
-- For portfolio demonstrations only.
-- Does not contain real network traffic.

BEGIN;

-- 1. Synthetic prediction history (30 records)
INSERT INTO public.ai_prediction_history (
    prediction,
    ddos_probability_percent,
    features,
    created_at
)
SELECT
    CASE
        WHEN n % 3 = 0 THEN 'DDoS'
        ELSE 'BENIGN'
    END,
    CASE
        WHEN n % 3 = 0 THEN 95.0 + (n % 5)
        ELSE 1.0 + (n % 8)
    END,
    jsonb_build_object(
        'demo', true,
        'sample_number', n,
        'source', 'synthetic_portfolio_data'
    ),
    NOW() - ((30 - n) * INTERVAL '2 hours')
FROM generate_series(1, 30) AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM public.ai_prediction_history
    WHERE features ->> 'source' = 'synthetic_portfolio_data'
);

-- 2. Synthetic batch analysis
INSERT INTO public.batch_analyses (
    filename,
    total_analyzed,
    benign_count,
    ddos_count,
    created_at
)
SELECT
    'demo_network_traffic.csv',
    12,
    8,
    4,
    NOW() - INTERVAL '1 day'
WHERE NOT EXISTS (
    SELECT 1
    FROM public.batch_analyses
    WHERE filename = 'demo_network_traffic.csv'
);

-- 3. Synthetic batch prediction results
INSERT INTO public.batch_prediction_results (
    batch_id,
    row_number,
    prediction,
    ddos_probability_percent
)
SELECT
    b.id,
    n,
    CASE
        WHEN n % 3 = 0 THEN 'DDoS'
        ELSE 'BENIGN'
    END,
    CASE
        WHEN n % 3 = 0 THEN 97.5
        ELSE 2.5
    END
FROM public.batch_analyses b
CROSS JOIN generate_series(1, 12) AS n
WHERE b.filename = 'demo_network_traffic.csv'
AND NOT EXISTS (
    SELECT 1
    FROM public.batch_prediction_results r
    WHERE r.batch_id = b.id
);

-- 4. Synthetic security alerts
INSERT INTO public.security_alerts (
    alert_type,
    severity,
    status,
    description,
    ddos_probability_percent,
    source,
    created_at,
    resolved_at
)
SELECT
    'DDoS',
    'Critical',
    'Active',
    'Synthetic demo: high-probability DDoS classification.',
    98.7,
    'demo_seed',
    NOW() - INTERVAL '3 hours',
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.security_alerts
    WHERE source = 'demo_seed'
);

INSERT INTO public.security_alerts (
    alert_type,
    severity,
    status,
    description,
    ddos_probability_percent,
    source,
    created_at,
    resolved_at
)
SELECT
    'DDoS',
    'High',
    'Active',
    'Synthetic demo: suspicious traffic classification.',
    87.4,
    'demo_seed',
    NOW() - INTERVAL '2 hours',
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.security_alerts
    WHERE source = 'demo_seed'
    AND severity = 'High'
);

INSERT INTO public.security_alerts (
    alert_type,
    severity,
    status,
    description,
    ddos_probability_percent,
    source,
    created_at,
    resolved_at
)
SELECT
    'DDoS',
    'Medium',
    'Resolved',
    'Synthetic demo: previously reviewed alert.',
    72.3,
    'demo_seed',
    NOW() - INTERVAL '1 day',
    NOW() - INTERVAL '20 hours'
WHERE NOT EXISTS (
    SELECT 1 FROM public.security_alerts
    WHERE source = 'demo_seed'
    AND status = 'Resolved'
);

COMMIT;
