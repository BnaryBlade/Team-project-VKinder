/* delete data from tables */
DELETE FROM users *;
-- WHERE user_id > 0;

/* inssert data into users */
INSERT INTO users (first_name, last_name, user_age, sex, city, vk_id, prf_link, interests)
VALUES ('igor_1', 'pavlov_1', 11, 1, 'town_1', 111111111, 'href_1', '{"семейное_положение": "холост"}'),
       ('igor_2', 'pavlov_2', 12, 1, 'town_2', 111111112, 'href_2', '{"семейное_положение": "женат"}'),
       ('igor_3', 'pavlov_3', 13, 1, 'town_3', 111111113, 'href_3', '{"семейное_положение": "в разводе"}'),
       ('igor_4', 'pavlov_4', 14, 1, 'town_4', 111111114, 'href_4', '{"семейное_положение": "холост"}'),
       ('igor_5', 'pavlov_5', 15, 1, 'town_5', 111111115, 'href_5', '{"семейное_положение": "холост"}');

/* inssert data into blacklist */   
INSERT INTO blacklist (vk_id)
VALUES (111111113),
       (111111114);

/* inssert data into photos */ 
INSERT INTO photos (photo_link, vk_id, user_mark)
VALUES ('href_1', 111111114, false),
       ('href_2', 111111115, true),
       ('href_2', 111111115, true);



/* inssert user first_data */
INSERT INTO users (first_name, last_name, vk_id, prf_link)
VALUES ('igor_01', 'pavlov_01', 111101111, 'href_01'),
       ('igor_02', 'pavlov_02', 111101112, 'href_02');

/* update user data */
UPDATE users
   SET interests = '{"семейное положение": "холост", "жанр музыки": "рок"}'
 WHERE vk_id = 111101112
--/* inssert interests */
--INSERT INTO users (interests)
--VALUES('')
--WHERE ;