DROP TABLE IF EXISTS boardgames CASCADE;
CREATE TABLE boardgames(
    bg_index INT,
    boardgameID INT PRIMARY KEY,
    boardgameRank FLOAT,
    boardgameName VARCHAR,
    boardgameLink VARCHAR,
    num_voters INT,
    categories VARCHAR, 
    machanics VARCHAR, 
    family VARCHAR,
    expansions VARCHAR,
    integrations VARCHAR,
    designers VARCHAR,
    publishers VARCHAR
);

\copy boardgames FROM '../data/boardgames_extend.csv' DELIMITER ',' CSV HEADER;

DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users(
  userName VARCHAR,
  num_ratings INT,
  userID INT PRIMARY KEY
);

\copy users FROM '../data/users.csv' DELIMITER ',' CSV HEADER;

DROP TABLE IF EXISTS ratings CASCADE;
CREATE TABLE ratings(
  boardgameID INT REFERENCES boardgames,
  rating FLOAT,
  userID INT REFERENCES users
);
  
\copy ratings FROM '../data/ratings_cleaned.csv' DELIMITER ',' CSV HEADER;

CREATE INDEX name_index ON users (userName);