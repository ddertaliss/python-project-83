DROP TABLE url_checks IF EXISTS;
DROP TABLE urls IF EXISTS;
CREATE TABLE urls (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255),
    created_at TIMESTAMP
);
CREATE TABLE url_checks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id BIGINT REFERENCES urls (id),
    status_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    created_at TIMESTAMP
);