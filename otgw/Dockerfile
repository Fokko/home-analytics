FROM alpine:latest

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev python3

RUN echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app/

CMD ["python3", "listen.py "]
