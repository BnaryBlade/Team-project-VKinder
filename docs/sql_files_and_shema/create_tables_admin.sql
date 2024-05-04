/* drop all tables */
DROP TABLE IF EXISTS
    clients,
    users,
    list_type,
    photos;



CREATE TABLE IF NOT EXISTS public.clients
(
    client_id integer NOT NULL DEFAULT nextval('clients_client_id_seq'::regclass),
    clt_vk_id integer NOT NULL,
    CONSTRAINT clients_pkey PRIMARY KEY (clt_vk_id)
);




CREATE TABLE IF NOT EXISTS public.users
(
    user_id integer NOT NULL DEFAULT nextval('users_user_id_seq'::regclass),
    usr_vk_id integer NOT NULL,
    first_name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    last_name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    prf_link text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (usr_vk_id)
)


CREATE TABLE IF NOT EXISTS public.list_type
(
    clt_vk_id integer NOT NULL,
    usr_vk_id integer NOT NULL,
    favorites boolean NOT NULL DEFAULT false,
    blacklist boolean NOT NULL DEFAULT false,
    CONSTRAINT list_type_pkey PRIMARY KEY (clt_vk_id, usr_vk_id),
    CONSTRAINT list_type_clt_vk_id_fkey FOREIGN KEY (clt_vk_id)
        REFERENCES public.clients (clt_vk_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT list_type_usr_vk_id_fkey FOREIGN KEY (usr_vk_id)
        REFERENCES public.users (usr_vk_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT check_list CHECK (favorites <> blacklist)
);


CREATE TABLE IF NOT EXISTS public.photos
(
    id integer NOT NULL DEFAULT nextval('photos_id_seq'::regclass),
    photo_id integer NOT NULL,
    owner_id integer NOT NULL,
    photo_link text COLLATE pg_catalog."default" NOT NULL,
    user_mark boolean NOT NULL DEFAULT false,
    CONSTRAINT photos_pkey PRIMARY KEY (photo_id),
    CONSTRAINT photos_owner_id_fkey FOREIGN KEY (owner_id)
        REFERENCES public.users (usr_vk_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);







