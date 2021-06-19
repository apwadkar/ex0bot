FROM python:3.8-alpine

WORKDIR /usr/server

# RUN apk add --no-cache --virtual .build-deps gcc musl-dev
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
# RUN apk del .build-deps

COPY ./ ./

# CMD [ "python", "app.py" ]
CMD [ "flask", "run", "--host=0.0.0.0", "--port=9007" ]