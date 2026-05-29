-- Altaria N1 — Polyglot persistence schemas
-- PostgreSQL (missions, fleets, audit) + TimescaleDB (telemetry, events)

-- ═══════════════════════════════════════════════════════════════════════════
-- PostgreSQL — operational state
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS fleets (
    fleet_id        VARCHAR(64) PRIMARY KEY,
    name            VARCHAR(256) NOT NULL,
    region          VARCHAR(64),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS uavs (
    uav_id          VARCHAR(64) PRIMARY KEY,
    fleet_id        VARCHAR(64) REFERENCES fleets(fleet_id),
    callsign        VARCHAR(128),
    vehicle_type    VARCHAR(32) DEFAULT 'multirotor',
    autopilot       VARCHAR(32) DEFAULT 'px4',
    edge_node_id    VARCHAR(64),
    status          VARCHAR(32) DEFAULT 'active',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS missions (
    mission_id      VARCHAR(64) PRIMARY KEY,
    fleet_id        VARCHAR(64) REFERENCES fleets(fleet_id),
    name            VARCHAR(256),
    intent          TEXT,
    status          VARCHAR(32) DEFAULT 'planned',
    semantic_objectives JSONB DEFAULT '[]',
    geofence        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mission_assignments (
    mission_id      VARCHAR(64) REFERENCES missions(mission_id),
    uav_id          VARCHAR(64) REFERENCES uavs(uav_id),
    role            VARCHAR(32) DEFAULT 'primary',
    PRIMARY KEY (mission_id, uav_id)
);

CREATE TABLE IF NOT EXISTS recovery_workflows (
    workflow_id     VARCHAR(64) PRIMARY KEY,
    uav_id          VARCHAR(64) REFERENCES uavs(uav_id),
    policy          VARCHAR(64) NOT NULL,
    severity        VARCHAR(32),
    status          VARCHAR(32) DEFAULT 'pending',
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    steps           JSONB DEFAULT '[]',
    metadata        JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS audit_commands (
    id              BIGSERIAL PRIMARY KEY,
    uav_id          VARCHAR(64) NOT NULL,
    command         VARCHAR(128) NOT NULL,
    source          VARCHAR(64),
    allowed         BOOLEAN,
    reason          VARCHAR(256),
    threat_score    FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    payload         JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_uav_time ON audit_commands(uav_id, created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- TimescaleDB — time-series (run on Timescale-enabled instance)
-- ═══════════════════════════════════════════════════════════════════════════

-- CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS telemetry_samples (
    time            TIMESTAMPTZ NOT NULL,
    uav_id          VARCHAR(64) NOT NULL,
    altitude_m      DOUBLE PRECISION,
    battery_pct     DOUBLE PRECISION,
    rpm             DOUBLE PRECISION,
    risk_value      DOUBLE PRECISION,
    anomaly_score   DOUBLE PRECISION,
    payload         JSONB
);

-- SELECT create_hypertable('telemetry_samples', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS risk_scores (
    time            TIMESTAMPTZ NOT NULL,
    uav_id          VARCHAR(64) NOT NULL,
    value           DOUBLE PRECISION,
    level           VARCHAR(16),
    r_mechanical    DOUBLE PRECISION,
    r_sensor        DOUBLE PRECISION,
    r_comms         DOUBLE PRECISION,
    r_ai            DOUBLE PRECISION,
    dominant_source VARCHAR(64)
);

-- SELECT create_hypertable('risk_scores', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS domain_events (
    time            TIMESTAMPTZ NOT NULL,
    event_id        UUID NOT NULL,
    event_type      VARCHAR(64) NOT NULL,
    uav_id          VARCHAR(64),
    fleet_id        VARCHAR(64),
    correlation_id  UUID,
    payload         JSONB
);

-- SELECT create_hypertable('domain_events', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS twin_snapshots (
    time            TIMESTAMPTZ NOT NULL,
    uav_id          VARCHAR(64) NOT NULL,
    cycle           INTEGER,
    system_state    VARCHAR(32),
    snapshot        JSONB NOT NULL
);

-- SELECT create_hypertable('twin_snapshots', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS predictions (
    time            TIMESTAMPTZ NOT NULL,
    uav_id          VARCHAR(64) NOT NULL,
    model_id        VARCHAR(64),
    battery_pred    DOUBLE PRECISION,
    rpm_pred        DOUBLE PRECISION,
    crash_probability DOUBLE PRECISION,
    confidence      DOUBLE PRECISION,
    uncertainty     DOUBLE PRECISION
);

-- SELECT create_hypertable('predictions', 'time', if_not_exists => TRUE);
