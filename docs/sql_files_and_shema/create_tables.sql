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
    PRIMARY KEY (client_id),
    client_id INTEGER NOT NULL
);



/* Table of users: */
CREATE TABLE IF NOT EXISTS Users (
    PRIMARY KEY (user_id),
    user_id    INTEGER      NOT NULL,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    prf_link   TEXT         NOT NULL
);

/* Table of list_type: */
CREATE TABLE IF NOT EXISTS List_type (
    PRIMARY KEY (client_id, user_id),
    client_id  INTEGER NOT NULL REFERENCES clients (client_id)
                       ON DELETE CASCADE ON UPDATE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users (user_id)
                       ON DELETE CASCADE ON UPDATE CASCADE,
    blacklist  BOOL    DEFAULT FALSE NOT NULL,
);

/* Table of users photos: */
CREATE TABLE IF NOT EXISTS Photos (
    PRIMARY KEY (photo_id),
	photo_id   INTEGER NOT NULL,
	owner_id   INTEGER NOT NULL REFERENCES Users (user_id)
	                   ON DELETE CASCADE ON UPDATE CASCADE,
	photo_link TEXT    NOT NULL,
	user_mark  BOOL    NOT NULL DEFAULT FALSE
);
