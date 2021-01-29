FROM python:3.7-slim

# get our dependencies
COPY ./requirements.txt /code/requirements.txt
WORKDIR /code

# install dependencies
RUN pip install -r requirements.txt

# get the rest of our code
COPY . /code

# setup flask parameters
ENV FLASK_APP /code/main.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5005

# run the app
# CMD gunicorn --config ./gunicorn.py --preload wsgi:app
CMD ["flask", "run"]
