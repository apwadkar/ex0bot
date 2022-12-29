FROM python:3.10-alpine

WORKDIR /usr/bot

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
RUN apk del .build-deps

COPY ./ ./

CMD [ "python", "bot.py" ]