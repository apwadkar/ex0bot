# Contributing

## Git Setup

Create a fork of the repo to track your own changes. When finished, submit a PR to this repo so I can take a look.
I'd prefer if you squash commits, but rebasing is also fine.

## Development Setup

You'll need a Discord bot application setup for a valid bot token. You'll also need a Redis server setup, there's
a pretty small footprint and doesn't take up much memory unless you have millions of users.

For a development setup, you'll need to create a `.env` file in both the `bot` and `serverless` folders.

In `bot`:

 - `DISCORD_TOKEN` - Token for your Discord bot
 - `REDIS_URL` - URL for your Redis server (needs to be in valid Redis URL format)
   - If you're using my [docker-compose.yml](https://github.com/apwadkar/ex0bot/blob/master/docker-compose.yml), the URL is `redis://redis-server:6379`

In `serverless`:

 - `REDIS_URL` - URL for your Redis server (same as above)

Development setup of the bot is handled by Docker, so all you need to do is run `docker compose up --build`

### Serverless Setup

For the API, I'm using SST (an extension of AWS Cloud Development Kit) to setup a serverless stack. To deploy,
you will need your own AWS account and AWS CLI setup. Once these are setup, you can simply run `yarn deploy` to
deploy the stack to the dev stage.

I'm trying to be as frugal as I can and using free tier everything so no one has to pay for any hosting.
