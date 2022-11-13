CREATE TABLE users (
    userID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(60) NOT NULL UNIQUE,
    joinDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    balance INT DEFAULT 100 NOT NULL,
    lastBetDate TIMESTAMP DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE bets (
    betID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    amountBet INT NOT NULL CHECK (amountBet > 0),
    odds INT,
    teamBetOn BOOL NOT NULL,
    timeBet TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    resolved BOOL NOT NULL DEFAULT 0,
    userID INT NOT NULL,
    gameID INT NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (gameID) REFERENCES games(gameID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE games (
    gameID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    teamNameZero VARCHAR(60) NOT NULL,
    gameStartTime TIMESTAMP NOT NULL,
    league VARCHAR(60) NOT NULL,
    teamNameOne VARCHAR(60) NOT NULL,
    postID VARCHAR(60),
    winner BOOL
);



CREATE TABLE messageLog(
    commentID VARCHAR(60) NOT NULL PRIMARY KEY, -- reddit comment ID 
    timeRead TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    truncBody VARCHAR(50) NOT NULL, -- reddit comment, truncated to 50 chars
    commandGiven VARCHAR(10) NOT NULL DEFAULT 'INVALID',
    respondedTo BOOL NOT NULL DEFAULT 0, -- if we've responded, default to False (0)
    postID VARCHAR(60) NOT NULL,
    userID INT NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(userID) ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE messageLog ADD CONSTRAINT username FOREIGN KEY (messageUsername) REFERENCES users (username);
ALTER TABLE messageLog ADD CONSTRAINT postID FOREIGN KEY (messagePostID) REFERENCES games(postID)


-- below is basic inserts for testing
INSERT INTO users (username) VALUES ('testname123');
INSERT INTO games (teamNameZero, gameStartTime, league, teamNameOne) VALUES ('Green Bay Packers', '2022-12-17 15:30:00', 'NFL', 'North Pole Elvish Diving Team');


INSERT INTO bets (amountBet, teamBetOn, userID, gameID) VALUES (100, 0, (SELECT userID FROM users WHERE username = 'testname123'), (SELECT gameID FROM games WHERE gameID = 1));





SELECT * FROM games WHERE gameStartTime > NOW() - INTERVAL 1 WEEK;



SELECT gameID FROM games WHERE postID = {postID} AND (OR teamNameZero)



#for BETS response

SELECT gameID, DAYNAME(gameStartTime) AS dayName
CASE WHEN teamBetOn = teamNameOne THEN 1 ELSE 0 END AS teamBool --teamBool is the new variable name and is returned, kinda like an 'if' then select
FROM games WHERE postID = {postID} AND (teamNameOne = {teamBetOn} OR teamNameZero = {teamBetOn}) 
AND (LOWER(dayName) LIKE '%{dayOfWeek.lower()}%') AND gameStartTime > NOW() AND gameStartTime < NOW() + INTERVAL 1 WEEK
