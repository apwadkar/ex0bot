FROM node:17-alpine

WORKDIR /usr/bot

COPY ./package.json ./yarn.lock ./
RUN yarn install

COPY ./ ./

# Register guild commands
RUN yarn register

CMD [ "yarn", "start" ]