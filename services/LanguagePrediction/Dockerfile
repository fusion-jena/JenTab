FROM python:3.7-slim

# get our dependencies
COPY ./requirements.txt /code/requirements.txt
WORKDIR /code

# install system level dependencies
RUN apt-get update && \
    apt-get -y install g++

# install dependencies
RUN pip install -r requirements.txt

# get the rest of our code
COPY . /code

# run the app
CMD gunicorn --config ./gunicorn.py --preload wsgi:app
