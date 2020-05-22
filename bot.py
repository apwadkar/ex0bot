import redis
import discord
from discord.ext import commands

# Settings
import settings

# Connect to Redis backend cache
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    # Confirm that we logged into the bot user successfully
    print(f'Logged on as {bot.user}!')

@bot.command(name="role")
async def role(context: commands.Context, arg):
    await context.send(arg)

@bot.command(name="announce")
async def announce(context: commands.Context, arg):
    await context.send(arg)

@bot.command(name="kick")
async def kick(context: commands.Context, arg):
    # print(arg)
    await context.send(arg)

@bot.event
async def on_message(message: discord.Message):
    # Ignore any messages from self
    if message.author != bot.user:
        # print('Message from {0.author}: {0.content}'.format(message))
        pass

@bot.event
async def on_member_add(member: discord.Member):
    # Restore all roles from Redis backend if an entry exists
    pass

@bot.event
async def on_member_remove(member: discord.Member):
    # TODO: Consider just making this a command in case of user leaving
    # Save all roles into the Redis backend
    # Format: roles:{user_id} as list containing all role ids
    # await add_roles(*[role_ids])
    pass

bot.run(settings.DISCORD_TOKEN)