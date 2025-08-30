CREATE TABLE IF NOT EXISTS saas_factory_experiments.experiment_events (
    event_id STRING NOT NULL,
    user_id STRING NOT NULL,
    experiment_key STRING NOT NULL,
    variation_id STRING NOT NULL,
    event_name STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    properties JSON
); 