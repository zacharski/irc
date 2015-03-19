DROP DATABASE IF EXISTS chat;
CREATE DATABASE  chat;
\c chat;
CREATE EXTENSION pgcrypto;
--
-- Table structure for table users
--

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id serial NOT NULL,
  username varchar(25) NOT NULL default '',
  password varchar(300) NOT NULL default '',
  PRIMARY KEY  (id)
) ;

--
-- Putting data into the users table
--

INSERT INTO users (username, password) VALUES 
('ryan', crypt('og123', gen_salt('bf'))),
('peter', crypt('laser', gen_salt('bf'))),
('ghost', crypt('spooky', gen_salt('bf'))),
('ghostbuster', crpyt('wygc', gen_salt('bf')));


--
-- Table structure for table messages
--

DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
  id serial NOT NULL,
  text varchar(300) NOT NULL default '',
  user_id int NOT NULL default '0',
  PRIMARY KEY  (id)
) ;

--
-- Putting data into the messages table
--

INSERT INTO messages (text, user_id) VALUES ('i wonder if we will pass this?', 1);
INSERT INTO messages (text, user_id) VALUES ('idk, man. this was really hard.', 2);
INSERT INTO messages (text, user_id) VALUES ('yeah, totally', 1);
INSERT INTO messages (text, user_id) VALUES ('you will never PASS!!!!', 3);
INSERT INTO messages (text, user_id) VALUES ('WTF', 2);
INSERT INTO messages (text, user_id) VALUES ('AHHHHHHHHHHHHH', 2);
INSERT INTO messages (text, user_id) VALUES ('RUN!!!', 1);
INSERT INTO messages (text, user_id) VALUES ('i aint afraid of no ghosts', 4);

