CREATE DATABASE intermediary_db;

\c intermediary_db

CREATE TABLE datasets (
    dataset_id VARCHAR(255) PRIMARY KEY,
    tables text[] NOT NULL DEFAULT '{}'
);

CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY
);

CREATE TABLE third_party (
    id VARCHAR(255) PRIMARY KEY
);

CREATE TABLE perms (
    dataset_id VARCHAR(255),
    third_party VARCHAR(255),
    allowed BOOLEAN,
    CONSTRAINT fk_third_party
        FOREIGN KEY(third_party)
            REFERENCES third_party(id)
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    created timestamp default current_timestamp,
    caller_id VARCHAR(255),
    target_id VARCHAR(255),
    msg_type VARCHAR(255),
    msg_content bytea
);

CREATE TABLE sample_dataset (
    target_id VARCHAR(255),
    val integer[]
);
