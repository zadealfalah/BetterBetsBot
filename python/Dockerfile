FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# COPY redditScripts.py redditScripts.py

COPY dbInteractions.py dbInteractions.py

#keep utils.py as last layer for now. most likely to be updated - layer caching
COPY utils.py utils.py

ENTRYPOINT [ "python", "" ] 