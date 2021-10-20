FROM python:3.7-slim

# get our dependencies
COPY ./requirements.txt /code/requirements.txt
WORKDIR /code

# install dependencies
RUN pip install -r requirements.txt

# get the rest of our code
COPY . /code

# run the app
# waitress-serve --host 0.0.0.0 --port=5100 wsgi:app
CMD gunicorn --config ./gunicorn.py --preload wsgi:app
