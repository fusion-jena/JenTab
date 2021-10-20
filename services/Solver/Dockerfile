FROM python:3.7-slim

# get our dependencies
COPY ./requirements.txt /code/requirements.txt
WORKDIR /code

# install gcc
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install -r requirements.txt && \
    python -m spacy download en

# get the rest of our code
COPY . /code

# setup flask parameters
ENV FLASK_APP /code/main.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000

# run the app
CMD ["flask", "run"]
