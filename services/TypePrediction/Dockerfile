FROM python:3.7-slim

# get our dependencies
COPY ./requirements.txt /code/requirements.txt
WORKDIR /code

# install dependencies
RUN pip install -r requirements.txt && \
    python -m spacy download en

# get the rest of our code
COPY . /code

# run the app
CMD gunicorn --config ./gunicorn.py --preload wsgi:app
