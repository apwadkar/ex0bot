import redis
import discord
from discord.ext import commands

class Counter(commands.Cog):
  def __init__(self, cache: redis.Redis, numpenalty: float = 0.5, teampenalty: float = 0.1):
    self.cache = cache
    self.numpenalty = numpenalty
    self.teampenalty = teampenalty

  async def countcheck(self, team: str, base: int, message: discord.Message, userteam: str):
    member = message.author
    if userteam != team:
      # TODO: 1 Warning to 10% reduction of counter
      await message.channel.send(f'{member.mention} You counted for the wrong team! This is a warning')
    lastright = int(self.cache.hget(f'counting:{message.guild.id}', key=team))
    newval = int(lastright) + 1
    if int(message.content, base=base) != int(lastright) + 1:
      # Wrong number inputted, half counter and restart
      await message.channel.send(f'{member.mention} messed up for team {team}!')
      newval = int(lastright / 2)
      # TODO: Don't hardcode these int -> string conversions
      newvalstr = ''
      if base == 10:
        newvalstr = f'{newval}'
      if base == 16:
        newvalstr = hex(newval)
      if base == 2:
        newvalstr = bin(newval)
      await message.channel.send(f'{team}: {newvalstr}')
    self.cache.hset(f'counting:{message.guild.id}', key=team, value=newval)
  
  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    # Ignore any messages from self
    member: discord.Member = message.author
    if member != message.guild.me:
      # Check whether the counting channel is linked
      channelid = self.cache.hget(f'counting:{message.guild.id}', key='channelid')
      if channelid:
        channel: discord.TextChannel = message.guild.get_channel(int(channelid))
        if message.channel == channel:
          # Get team role of user
          team = ''
          for role in member.roles:
            if role.name == 'Decimal' or role.name == 'Hexadecimal' or role.name == 'Binary':
              team = role.name
              break
          if team:
            if message.content.startswith('0x'):
              await self.countcheck('Hexadecimal', 16, message, team)
            if message.content.startswith('0b'):
              await self.countcheck('Binary', 2, message, team)
            elif message.content.isnumeric():
              await self.countcheck('Decimal', 10, message, team)
          else:
            message.channel.send(f'{member} doesn\'t have a valid team! {member.mention} Choose a role from the channel!')

  @commands.command(name='countlink')
  @commands.has_guild_permissions(administrator=True)
  async def countlink(self, context: commands.Context, channel: discord.TextChannel):
    await context.message.delete()
    self.cache.hset(f'counting:{context.guild.id}', key='channelid', value=channel.id)
    await context.send(f'Linked {channel} for counting')
  
  @commands.command(name='countsetpen')
  @commands.has_guild_permissions(administrator=True)
  async def countsetpen(self, context: commands.Context, numpenalty: float = -1.0, teampenalty: float = -1.0):
    await context.message.delete()
    if numpenalty >= 0.0:
      if numpenalty <= 1.0:
        self.numpenalty = numpenalty
      else:
        await context.send('Invalid wrong number penalty')
    if teampenalty >= 0.0:
      if teampenalty <= 1.0:
        self.teampenalty = teampenalty
      else:
        await context.send('Invalid wrong team penalty')
  
  @commands.command(name='countset')
  @commands.has_guild_permissions(administrator=True)
  async def countset(self, context: commands.Context, deci: int = -1, hexa: int = -1, bina: int = -1):
    await context.message.delete()
    if deci >= 0:
      self.cache.hset(f'counting:{context.guild.id}', key='Decimal', value=deci)
    if hexa >= 0:
      self.cache.hset(f'counting:{context.guild.id}', key='Hexadecimal', value=hexa)
    if bina >= 0:
      self.cache.hset(f'counting:{context.guild.id}', key='Binary', value=bina)
    await context.send(f'Set values for each team: Decimal: {deci}, Hexadecimal: {hex(hexa)}, Binary: {bin(bina)}')
  
  @commands.command(name='countteamadd')
  @commands.has_guild_permissions(administrator=True)
  async def counteamadd(self, context: commands.Context, name: str, prefix: str, base: int):
    # TODO: Implement dynamic teams not hardcoded
    await context.message.delete()
    await context.send('Command unimplemented!')