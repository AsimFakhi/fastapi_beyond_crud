INSERT INTO user_accounts (uid, username, first_name, last_name, email, password_hash, role, is_verified)
VALUES (gen_random_uuid(), 'admin1', 'Admin', 'User', 'admin@mail.com', 'hashed_pw', 'admin', true);

SELECT * FROM user_accounts;
DELETE FROM user_accounts;

-- Author
INSERT INTO user_accounts (uid, username, first_name, last_name, email, password_hash, role, is_verified)
VALUES (gen_random_uuid(), 'author1', 'Author', 'User', 'author@mail.com', 'hashed_pw', 'author', true);

-- Regular User
INSERT INTO user_accounts (uid, username, first_name, last_name, email, password_hash, role, is_verified)
VALUES (gen_random_uuid(), 'user1', 'Regular', 'User', 'user@mail.com', 'hashed_pw', 'user', true);