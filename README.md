# BetterBetsBot
## This is a Reddit bot for sports betting with a database sitting on Pythonanywhere.  
The database schema is located in seddDB.sql and the brunt of the code is currently in utils.py.
As the work continues it is expected that utils.py will be split as it is already getting quite large.  For now it holds almost all of the reddit bot creation and database manipulation code.  Some specific cases exist in their own .py files (e.g. betsScripts.py which holds some updates for the bets table).  Organzing these code snippets is lower in priority at the moment but will be addressed before a full launch.
