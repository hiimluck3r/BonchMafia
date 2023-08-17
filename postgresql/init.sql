CREATE TABLE admins(id SERIAL PRIMARY KEY, userid BIGINT, nickname VARCHAR);
CREATE TABLE banned(id SERIAL PRIMARY KEY, userid BIGINT, reason VARCHAR, adminid BIGINT);
CREATE TABLE games(id SERIAL PRIMARY KEY, gamedate VARCHAR, gamehost VARCHAR, don VARCHAR, sheriff VARCHAR, mafia VARCHAR, citizen VARCHAR, winner VARCHAR);
CREATE TABLE users(id SERIAL PRIMARY KEY, userid BIGINT, don BIGINT, don_total BIGINT, mafia BIGINT, mafia_total BIGINT, sheriff BIGINT, sheriff_total BIGINT, citizen BIGINT, citizen_total BIGINT, won BIGINT, lost BIGINT, mentor VARCHAR, nickname VARCHAR);

INSERT INTO users(userid, don, don_total, mafia, mafia_total, sheriff, sheriff_total, citizen, citizen_total, won, lost, mentor, nickname) VALUES (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'blank', 'blank');
INSERT INTO users(userid, don, don_total, mafia, mafia_total, sheriff, sheriff_total, citizen, citizen_total, won, lost, mentor, nickname) VALUES (-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', '-');