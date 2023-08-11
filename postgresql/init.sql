CREATE TABLE admins(id SERIAL PRIMARY KEY, userid BIGINT, nickname VARCHAR);
CREATE TABLE banned(id SERIAL PRIMARY KEY, userid BIGINT, reason VARCHAR, adminid BIGINT);
CREATE TABLE games(id SERIAL PRIMARY KEY, gamedate VARCHAR, gamehost VARCHAR, players VARCHAR, winner BOOLEAN);
CREATE TABLE users(id SERIAL PRIMARY KEY, userid BIGINT, don BIGINT, mafia BIGINT, sheriff BIGINT, citizen BIGINT, won BIGINT, lost BIGINT, mentor VARCHAR, nickname VARCHAR);