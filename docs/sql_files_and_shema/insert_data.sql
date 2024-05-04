/* delete data from tables */
--DELETE FROM users *;
-- WHERE user_id > 0;


--DELETE FROM clients
-- WHERE clt_vk_id = 111111114;
-- 
--DELETE FROM users AS u
-- WHERE u.usr_vk_id NOT IN
--       (SELECT l.usr_vk_id FROM list_type AS l);


DELETE FROM clients *;
DELETE FROM users *;
--DELETE FROM list_type *;
--DELETE FROM photos *;

INSERT INTO clients (clt_vk_id)
VALUES (111111111),
       (111111112),
       (111111113),
       (111111114),
       (111111115);

INSERT INTO users (usr_vk_id, first_name, last_name, prf_link)
VALUES (111101111, 'igor_1', 'pavlov_1', 'href_1'),
       (211101111, 'igor_2', 'pavlov_2', 'href_2'),
       (311101111, 'igor_3', 'pavlov_3', 'href_3'),
       (411101111, 'igor_4', 'pavlov_4', 'href_4'),
       (511101111, 'igor_5', 'pavlov_5', 'href_5');
       
INSERT INTO list_type (clt_vk_id, usr_vk_id, favorites, blacklist)
    VALUES (111111111, 111101111, FALSE, TRUE),
           (111111112, 211101111, FALSE, TRUE),
           (111111113, 311101111, TRUE, FALSE),
           (111111114, 411101111, TRUE, FALSE),
           (111111115, 511101111, TRUE, FALSE);

INSERT INTO photos (photo_id, owner_id, photo_link)
VALUES (111, 111101111, 'href_11'),
       (112, 211101111, 'href_12'),
       (113, 311101111, 'href_13'),
       (114, 411101111, 'href_14'),
       (115, 511101111, 'href_15');

