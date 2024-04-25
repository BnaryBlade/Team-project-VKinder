/* drop table cascade */
--DROP TABLE IF EXISTS users CASCADE;

/* drop all tables */
DROP TABLE IF EXISTS
    users,
    blacklist,
    photos;

/* creating tables */
/* Table of users: */
CREATE TABLE IF NOT EXISTS Users (
    PRIMARY KEY (user_id),
    user_id    SERIAL       NOT NULL,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    user_age   SMALLINT     NULL,
               CONSTRAINT users_age_check
               CHECK (user_age BETWEEN 1 AND 120) NOT VALID,
    sex        SMALLINT     DEFAULT 0 NOT NULL,
               CONSTRAINT users_sex_check 
               CHECK (sex BETWEEN 0 AND 2) NOT VALID,
    city       VARCHAR(100) NULL,
    vk_id      INTEGER      UNIQUE NOT NULL,
    prf_link   TEXT         NOT NULL,
    interests  JSON         NULL,
    favorites  BOOL         DEFAULT FALSE NOT NULL
);

/* Table of users in blacklist: */
CREATE TABLE IF NOT EXISTS Blacklist (
    PRIMARY KEY (id),
    id    SERIAL  NOT NULL,
    vk_id INTEGER UNIQUE NOT NULL REFERENCES users (vk_id)
                  ON DELETE CASCADE ON UPDATE CASCADE
);

/* Table of users photos: */
CREATE TABLE IF NOT EXISTS Photos (
    PRIMARY KEY (photo_id),
	photo_id   SERIAL  NOT NULL,
	photo_link TEXT    NOT NULL,
	vk_id      INTEGER NOT NULL REFERENCES users (vk_id)
	           ON DELETE CASCADE ON UPDATE CASCADE,
	user_mark  BOOL    NOT NULL DEFAULT FALSE
);
