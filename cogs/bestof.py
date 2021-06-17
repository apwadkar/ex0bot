import redis
import discord
from discord.ext import commands
from functools import reduce
from typing import List
from utils.logs import Logger


def bestof_key(guild_id: int) -> str:
    return f'bestof:{guild_id}'


class Bestof(commands.Cog):
    def __init__(self, bot: discord.Client, cache: redis.Redis, logger: Logger):
        self.bot = bot
        self.cache = cache
        self.logger = logger
    
    def enough_reacts(self, reactions: List[discord.Reaction], key: str) -> bool:
        ismember = lambda react: self.cache.sismember(f'{key}:emojis', str(react))
        threshold = int(self.cache.hget(key, 'cutoff'))
        filtered = [r for r in reactions if r.count >= threshold and ismember(r)]
        return len(filtered) != 0

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        key = bestof_key(payload.guild_id)
        if bool(self.cache.sismember(f'{key}:emojis', str(payload.emoji))):
            channel: discord.TextChannel = await self.bot.fetch_channel(payload.channel_id)
            message: discord.Message = await channel.fetch_message(payload.message_id)
            if self.enough_reacts(message.reactions, key) and not bool(self.cache.hexists(key, message.id)):
                await self.post_message(message, message.author, message.guild)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        key = bestof_key(payload.guild_id)
        if bool(self.cache.sismember(f'{key}:emojis', str(payload.emoji))):
            channel: discord.TextChannel = await self.bot.fetch_channel(payload.channel_id)
            message: discord.Message = await channel.fetch_message(payload.message_id)
            if not self.enough_reacts(message.reactions, key):
                await self.remove_embed(message.id, message.guild)
                
    async def post_message(self, bomsg: discord.Message, author: discord.Member, guild: discord.Guild):
        key = bestof_key(guild.id)
        self.cache.hincrby(key, 'count', 1)
        count = int(self.cache.hget(key, 'count'))
        embed = discord.Embed(
            title = f'Best of {guild.name} #{count}',
            description = bomsg.content,
            url = bomsg.jump_url,
            timestamp = bomsg.created_at,
            color = discord.Color.random()
        ).set_author(name=author.name, icon_url=author.avatar_url)
        # Add any attachments as links in fields
        image_set = False
        for i, attach in enumerate(bomsg.attachments):
            if not image_set and attach.content_type.startswith('image'):
                embed = embed.set_image(url=attach.url)
                image_set = True
            embed = embed.add_field(name=f'Attachment {i}', value=attach.url)

        channel_id = int(self.cache.hget(key, 'channel'))
        if bomsg.channel.id != channel_id:
            channel: discord.TextChannel = guild.get_channel(channel_id)
            message: discord.Message = await channel.send(embed=embed)
            embed.set_footer(text=f'Original ID: {bomsg.id} | Embed ID: {message.id}')
            await message.edit(embed=embed)
            self.cache.hset(key, bomsg.id, message.id)

    async def remove_embed(self, message_id: int, guild: discord.Guild):
        key = bestof_key(guild.id)
        embed_id = self.cache.hget(key, message_id)
        if embed_id:
            embed_id = int(embed_id)
            bochannel: discord.TextChannel = guild.get_channel(int(self.cache.hget(key, 'channel')))
            self.cache.hdel(key, message_id)
            await (await bochannel.fetch_message(embed_id)).delete()

    @commands.group(name='bestof')
    @commands.has_guild_permissions(administrator=True)
    async def bestof(self, context: commands.Context):
        await context.message.delete()
        if not context.invoked_subcommand:
            await context.send('Invalid bestof subcommand')

    @bestof.command(name='post')
    @commands.has_guild_permissions(administrator=True)
    async def post(self, context: commands.Context, message: discord.Message):
        await self.post_message(message, message.author, context.guild)
        await context.send(f'Force pushed {message.id} to bestof channel')

    @bestof.command(name='link')
    async def link(self, context: commands.Context, channel: discord.TextChannel):
        self.cache.hset(bestof_key(context.guild.id), 'channel', channel.id)
        await context.send(f'{channel.mention} has been linked for bestof')

    @bestof.command(name='unlink')
    async def unlink(self, context: commands.Context, channel: discord.TextChannel):
        self.cache.hdel(bestof_key(context.guild.id), 'channel')
        await context.send(f'{channel.mention} has been unlinked for bestof')

    @bestof.command(name='addemojis')
    async def add_emoji(self, context: commands.Context, *emojis):
        for emoji in emojis:
            self.cache.sadd(f'{bestof_key(context.guild.id)}:emojis', f'{emoji}')
        await context.send(f'{", ".join(emojis)} have been set as the starring emoji for this server.')
    
    @bestof.command(name='delemojis')
    async def del_emoji(self, context: commands.Context, *emojis):
        for emoji in emojis:
            self.cache.srem(f'{bestof_key(context.guild.id)}:emojis', f'{emoji}')
        await context.send(f'{", ".join(emojis)} has been removed as the starring emoji for this server.')

    @bestof.command(name='cutoff')
    async def threshold(self, context: commands.Context, cutoff: int):
        self.cache.hset(bestof_key(context.guild.id), 'cutoff', cutoff)
        await context.send(f'Threshold for starring messages is set to {cutoff}')
