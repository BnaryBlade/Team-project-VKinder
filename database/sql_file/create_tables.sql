/* drop all tables */
DROP TABLE IF EXISTS
    users,
    blacklist,
    photos;

/* creating tables */
/* Table of users: */
CREATE TABLE IF NOT EXISTS Users (
    user_id    SERIAL          NOT null,
    first_name VARCHAR(50)     NOT NULL,
    last_name  VARCHAR(50)     NOT NULL,
    user_age   SMALLINT        DEFAULT NULL,
    sex        SMALLINT        NOT NULL DEFAULT 0,
    city       VARCHAR(100)    DEFAULT NULL, 
    vk_id      INTEGER         NOT NULL,
    prf_link   TEXT            NOT NULL,
    interests  JSON            DEFAULT NULL,
    favorites  BOOL            NOT NULL DEFAULT FALSE,
    CONSTRAINT users_pkey      PRIMARY KEY (user_id),
    CONSTRAINT users_vk_id_key UNIQUE (vk_id)
);

/* Table of users in blacklist: */
CREATE TABLE IF NOT EXISTS Blacklist (
    id         SERIAL    NOT NULL,
    user_id    INTEGER   NOT NULL,
    CONSTRAINT blacklist_pkey PRIMARY KEY (id),
    CONSTRAINT blacklist_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

/* Table of users photos: */
CREATE TABLE IF NOT EXISTS Photos (
	photo_id   SERIAL  NOT NULL,
	photo_link TEXT    NOT NULL,
	user_id    INTEGER NOT NULL,
	user_mark  BOOL    NOT NULL DEFAULT FALSE,
    CONSTRAINT photos_pkey PRIMARY KEY (photo_id),
    CONSTRAINT photos_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
