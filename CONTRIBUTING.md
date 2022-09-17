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

Development setup of the bot is handled by Docker, so all you need to do is run `docker compose up --build`