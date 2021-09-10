FROM node:16-alpine

WORKDIR /usr/bot

COPY ./package.json ./yarn.lock ./
RUN yarn install

COPY ./ ./

CMD [ "yarn", "start" ]