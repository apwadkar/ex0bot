# Ex0bot

A simple Discord bot I made for my Discord server. It takes care of simple moderation tasks, as well as including some fun features like Karma and a Best Of.

This project uses [discord.py](https://github.com/Rappatz/discord.py) as a wrapper for the Discord API and a Redis backend for simple data storage.

## Features

 - Role management
 - Moderation logging
 - Accouncements
 - Voice Channel (VC) management
   - Temporary VCs
 - Karma system
 - "Starboard" Best of
 - Counting game
 - Polls

### Planned Features

With the new 2.0 version of discord.py, I'm hoping to add some cool interactions like slash commands and message components to enhance existing features or make new ones.

## Deploying

You'll need a Discord bot application setup for a valid bot token. You'll also need a Redis server setup, there's
a pretty small footprint and doesn't take up much memory unless you have millions of users.

For a production setup, you'll need to find a hosting platform like Heroku. I'm using Heroku, and I have all the files necessary for setting that up in the repo.
You'll need to add a Redis add-on, or specify the URL in environment variables (as `REDIS_URL`). You'll also need to set the `DISCORD_TOKEN` in environment variables.

I've tried to make this as server agnostic as I could, but if there's any feature that doesn't work properly, please [create an issue](https://github.com/apwadkar/ex0bot/issues/new) so I can look into it.