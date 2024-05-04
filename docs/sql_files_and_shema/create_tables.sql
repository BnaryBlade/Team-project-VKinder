/* drop table cascade */
--DROP TABLE IF EXISTS users CASCADE;

/* drop all tables */
DROP TABLE IF EXISTS
    clients,
    users,
    list_type,
    photos;

/* creating tables */
/* Table of clients: */
CREATE TABLE IF NOT EXISTS Clients (
    PRIMARY KEY (clt_vk_id),
    client_id SERIAL  NOT NULL,
    clt_vk_id INTEGER NOT NULL
);



/* Table of users: */
CREATE TABLE IF NOT EXISTS Users (
    PRIMARY KEY (usr_vk_id),
    user_id    SERIAL       NOT NULL,
    usr_vk_id  INTEGER      UNIQUE NOT NULL,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    prf_link   TEXT         NOT NULL
);

/* Table of list_type: */
CREATE TABLE IF NOT EXISTS List_type (
    PRIMARY KEY (clt_vk_id, usr_vk_id),
    clt_vk_id  INTEGER NOT NULL REFERENCES clients (clt_vk_id)
                       ON DELETE CASCADE ON UPDATE CASCADE,
    usr_vk_id  INTEGER NOT NULL REFERENCES users (usr_vk_id)
                       ON DELETE CASCADE ON UPDATE CASCADE,
    favorites BOOL    DEFAULT FALSE NOT NULL,
    blacklist  BOOL    DEFAULT FALSE NOT NULL,
               CONSTRAINT check_list
               CHECK (favorites != blacklist)
);

/* Table of users photos: */
CREATE TABLE IF NOT EXISTS Photos (
    PRIMARY KEY (photo_id),
    id         SERIAL  NOT NULL,
	photo_id   INTEGER UNIQUE NOT NULL,
	owner_id   INTEGER NOT NULL REFERENCES Users (usr_vk_id)
	                   ON DELETE CASCADE ON UPDATE CASCADE,
	photo_link TEXT    NOT NULL,
	user_mark  BOOL    NOT NULL DEFAULT FALSE
);
