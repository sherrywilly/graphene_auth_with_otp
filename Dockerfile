FROM  python:3

ENV PYTHONUNBUFFERED 1
WORKDIR /app
ADD . /app
COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt
EXPOSE 8000
COPY . /
