/* delete data from tables */
--DELETE FROM users *;
-- WHERE user_id > 0;


--DELETE FROM clients
-- WHERE clt_vk_id = 111111114;
-- 
--DELETE FROM users AS u
-- WHERE u.usr_vk_id NOT IN
--       (SELECT l.usr_vk_id FROM list_type AS l);


DELETE FROM list_type *;
DELETE FROM photos *;
DELETE FROM clients *;
DELETE FROM users *;


INSERT INTO clients (client_id)
VALUES (111111111),
       (111111112),
       (111111113),
       (111111114),
       (111111115),
       (861256395);

INSERT INTO users (user_id, first_name, last_name, prf_link)
VALUES (111101111, 'igor_1', 'pavlov_1', 'href_1'),
       (211101111, 'igor_2', 'pavlov_2', 'href_2'),
       (311101111, 'igor_3', 'pavlov_3', 'href_3'),
       (411101111, 'igor_4', 'pavlov_4', 'href_4'),
       (511101111, 'igor_5', 'pavlov_5', 'href_5');
       
INSERT INTO list_type (client_id, user_id, blacklist)
    VALUES (111111111, 111101111, TRUE),
           (861256395, 211101111, TRUE),
           (861256395, 311101111, FALSE),
           (111111114, 411101111, TRUE),
           (861256395, 511101111, FALSE);

INSERT INTO photos (photo_id, owner_id, photo_link, user_mark)
VALUES (111, 111101111, 'href_11', FALSE),
       (112, 211101111, 'href_12', FALSE),
       (113, 111101111, 'href_13', FALSE),
       (114, 411101111, 'href_14', FALSE),
       (115, 411101111, 'href_15', FALSE);

