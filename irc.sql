DROP DATABASE IF EXISTS irc_db;
CREATE DATABASE irc_db;
\c irc_db;

CREATE TABLE IF NOT EXISTS users (
	id serial,
	username varchar(30),
	password varchar(30),
	PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS messages (
	message_id serial,
	original_poster_id int NOT NULL,
	message_content bytea,
	PRIMARY KEY (message_id)
);

