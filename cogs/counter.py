import redis
import discord
from discord.ext import commands

def tobasestring(val: int, base: int):
  # TODO: Don't hardcode these int -> string conversions
  if base == 10:
    return f'{val}'
  if base == 16:
    return hex(val)
  if base == 2:
    return bin(val)

class Counter(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache
    self.basemap = {
      'Decimal': 10,
      'Hexadecimal': 16,
      'Binary': 2
    }

  async def countcheck(self, team: str, base: int, message: discord.Message, userteam: str):
    member = message.author
    if userteam != team:
      # TODO: 1 Warning to 10% reduction of counter
      warningset = self.cache.hget(f'counting:{message.guild.id}', key=f'warn:{message.author.id}')
      if warningset and int(warningset) == 1:
        teampenalty = float(self.cache.hget(f'counting:{message.guild.id}', key='teampenalty'))
        await message.channel.send(f'{member.mention} You counted for the wrong team! Since you were already warned, your team gets a {teampenalty * 100}% deduction.')
        teamlast = int(self.cache.hget(f'counting:{message.guild.id}', key=userteam))
        newteam = int(teamlast * (1 - teampenalty))
        await message.channel.send(f'{userteam}: {tobasestring(newteam, self.basemap[userteam])}')
      else:
        self.cache.hset(f'counting:{message.guild.id}', key=f'warn:{message.author.id}', value=1)
        await message.channel.send(f'{member.mention} You counted for the wrong team! This is a warning.')
    lastright = int(self.cache.hget(f'counting:{message.guild.id}', key=team))
    newval = int(lastright) + 1
    if int(message.content, base=base) != int(lastright) + 1:
      # Wrong number inputted => deduct counter
      await message.channel.send(f'{member.mention} messed up for team {team}!')
      newval = int(lastright * (1 - float(self.cache.hget(f'counting:{message.guild.id}', key='numpenalty'))))
      await message.channel.send(f'{team}: {tobasestring(newval, self.basemap[team])}')
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
    self.cache.hset(f'counting:{context.guild.id}', key='numpenalty', value=0.5)
    self.cache.hset(f'counting:{context.guild.id}', key='teampenalty', value=0.1)
    await context.send(f'Linked {channel} for counting')
  
  @commands.command(name='countsetpen')
  @commands.has_guild_permissions(administrator=True)
  async def countsetpen(self, context: commands.Context, numpenalty: float = -1.0, teampenalty: float = -1.0):
    await context.message.delete()
    if numpenalty >= 0.0:
      if numpenalty <= 1.0:
        self.cache.hset(f'counting:{context.guild.id}', key='numpenalty', value=numpenalty)
      else:
        await context.send('Invalid wrong number penalty')
    if teampenalty >= 0.0:
      if teampenalty <= 1.0:
        self.cache.hset(f'counting:{context.guild.id}', key='teampenalty', value=teampenalty)
      else:
        await context.send('Invalid wrong team penalty')
    await context.send(f'Penalty values adjusted')
  
  @commands.command(name='countgetpen')
  async def countgetpen(self, context: commands.Context):
    await context.message.delete()
    numpenalty = float(self.cache.hget(f'counting:{context.guild.id}', key='numpenalty'))
    teampenalty = float(self.cache.hget(f'counting:{context.guild.id}', key='teampenalty'))
    await context.send(f'Current penalty values: Wrong number: {numpenalty * 100}%, Wrong team: {teampenalty * 100}%')

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
  
  @commands.command(name='countget')
  @commands.has_guild_permissions(administrator=True)
  async def countget(self, context: commands.Context):
    await context.message.delete()
    deci = int(self.cache.hget(f'counting:{context.guild.id}', key='Decimal'))
    hexa = int(self.cache.hget(f'counting:{context.guild.id}', key='Hexadecimal'))
    bina = int(self.cache.hget(f'counting:{context.guild.id}', key='Binary'))
    await context.send(f'Current values: Decimal: {deci}, Hexadecimal: {hex(hexa)}, Binary: {bin(bina)}')
  
  @commands.command(name='countteamadd')
  @commands.has_guild_permissions(administrator=True)
  async def counteamadd(self, context: commands.Context, name: str, prefix: str, base: int):
    # TODO: Implement dynamic teams not hardcoded
    await context.message.delete()
    await context.send('Command unimplemented!')