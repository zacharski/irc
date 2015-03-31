DROP DATABASE IF EXISTS irc_db;
CREATE DATABASE irc_db;
\c irc_db

CREATE TABLE users (
	id serial,
	username varchar(30),
	password varchar(30),
	PRIMARY KEY (id)
);

CREATE TABLE rooms (
	id serial UNIQUE,
	roomname varchar(30),
/*	user_in_room varchar(30), */
	PRIMARY KEY (id)
);

CREATE TABLE subscriptions (
	id serial,
	room_id int NOT NULL,
	user_id int NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE messages (
	message_id serial,
	original_poster_id int NOT NULL,
	message_content VARCHAR(250),
	room_id int NOT NULL,
	PRIMARY KEY (message_id)
);

INSERT INTO users (id, username, password) 
VALUES 
(DEFAULT, 'SpiderBall', 'sb'), 
(DEFAULT, 'MidnaPeach', 'mp'),
(DEFAULT, 'lz', 'lz');

INSERT INTO rooms (id, roomname)
VALUES
(DEFAULT, 'General'),
(DEFAULT, 'Happy'),
(DEFAULT, 'Sad'),
(DEFAULT, 'Hungry');


INSERT INTO subscriptions (id, room_id, user_id)
VALUES
(DEFAULT, 1, 1),
(DEFAULT, 1, 2),
(DEFAULT, 1, 3),
(DEFAULT, 2, 1),
(DEFAULT, 3, 2),
(DEFAULT, 4, 1),
(DEFAULT, 4, 2),
(DEFAULT, 3, 3);
/* sb is subscribed to happy hungry and general 
   mp is subscribed to general sad and hungry 
   lz is subscribed to general and sad */
