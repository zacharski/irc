DROP DATABASE IF EXISTS irc_db;
CREATE DATABASE irc_db;
\c irc_db;

create user irc_user with password 'irc';
grant select, insert on irc_db to irc_user;
grant all on sequence users_id_seq to irc_user;

CREATE TABLE IF NOT EXISTS users (
	id serial,
	username varchar(30),
	password varchar(30),
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS rooms (
	id serial,
	roomname varchar(30),
	user_in_room varchar(30),
	PRIMARY KEY (id)
);



CREATE TABLE IF NOT EXISTS messages (
	message_id serial,
	original_poster_id int NOT NULL,
	message_content VARCHAR(250),
	room_id int NOT NULL,
	PRIMARY KEY (message_id)
);

INSERT INTO users (id, username, password) 
VALUES 
(DEFAULT, 'SpiderBall', 'sb'), 
(DEFAULT, 'MidnaPeach', 'mp');
