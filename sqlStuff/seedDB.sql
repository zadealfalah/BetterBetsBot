
-- I think that at the moment the way bets are handled means someone can place a bet before odds
-- are updated meaning it's feasible that someone bets an amount > their total balance
-- fix this in SQL or python? where?
-- add unique constraint to (userID, gameID) to stop mutliple bets on a single game
-- would stop us from having to change things in python
-- add unique constraint to (gameID, gameStartTime)
-- stops duplicate games from being made on accident

CREATE TABLE users (
userID INT PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(60) UNIQUE NOT NULL,
joinDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
balance INT NOT NULL DEFAULT 100,
nWins INT NOT NULL DEFAULT 0,
nLosses INT NOT NULL DEFAULT 0
);

CREATE TABLE user_last_bet (
userID INT PRIMARY KEY,
lastBetDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE games (
gameID INT PRIMARY KEY AUTO_INCREMENT,
teamNameZero VARCHAR(60) NOT NULL,
gameStartTime TIMESTAMP NOT NULL,
league VARCHAR(60) NOT NULL,
teamNameOne VARCHAR(60) NOT NULL,
winner BOOL
);

CREATE TABLE game_posts (
gameID INT PRIMARY KEY,
postID VARCHAR(60) NOT NULL,
FOREIGN KEY (gameID) REFERENCES games(gameID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE bets (
betID INT PRIMARY KEY AUTO_INCREMENT,
amountBet INT NOT NULL CHECK (amountBet > 0),
odds INT,
teamBetOn BOOL NOT NULL,
timeBet TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
resolved BOOL NOT NULL DEFAULT 0,
username VARCHAR(60) UNIQUE NOT NULL,
gameID INT NOT NULL,
FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
FOREIGN KEY (gameID) REFERENCES games(gameID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE messageLog(
commentID VARCHAR(60) PRIMARY KEY,
timeRead TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
truncBody VARCHAR(60) NOT NULL,
commandGiven VARCHAR(60) NOT NULL DEFAULT 'INVALID',
respondedTo BOOL NOT NULL DEFAULT 0,
postID VARCHAR(60),
username VARCHAR(60) UNIQUE NOT NULL,
gameID INT,
FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
FOREIGN KEY (gameID) REFERENCES games(gameID) ON DELETE CASCADE ON UPDATE CASCADE,
FOREIGN KEY (postID) REFERENCES game_posts(postID) ON DELETE CASCADE ON UPDATE CASCADE
);