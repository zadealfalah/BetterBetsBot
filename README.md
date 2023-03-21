# BetterBetsBot - Reddit Bot (WORK IN PROGRESS)
Reddit bot for sports betting

## Table of contents
* [General Info](#general-info)
* [Technologies](#technologies)
* [Features](#features)
* [Things To Do](#things-to-do)

## General Info
This is a reddit bot for sports betting.  It is currently inactive, but will hopefully be hosted on various sports subreddits pending their approval and the completion of the project.

The bot will create a post each week per subreddit in which it will list out that weeks' games.  Top-level comments within that post containing the keyphrase !BB interact with the bot.  See [Features](#features) for more.

## Technologies
- MySQL
- python (pandas, praw, pymysql, etc.)
- docker

## Features
To interact with the bot, type !BB {command} {opt1} {opt2} ... {optN}

The optional addendums here come from things like betting, where you want to specify how much and for whom you are betting.  Capitalization does not matter.

Current commands with examples:
- REGISTER:  !BB register   - This registers the user to the bot
- HELP:  !BB HELP  - This prints the currently supported commands with a few examples
- BET:  !BB bet 500 Packers     - This places a bet for 500 on the Packers game this week
- BALANCE:  !BB BALANCE     - This checks your balance
- WINLOSS:  !BB WinLoss     - This checks your win/loss ratio
- TOP5: !BB TOP5    - This checks the current top5 betters

Note that other commands currently return an error message.


## Things To Do
- Decide where to host the database
- Decide on whether top5 is based on current balance, win/loss, or what
- Contact reddit mods for possible subreddits
- Decide on how/when to calculate odds, or if we want them at all for 1st iteration
- May change how SQL statements are handled
