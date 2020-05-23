import redis
import discord
from discord.ext import commands

class Counter(commands.Cog):
  def __init__(self, cache: redis.Redis):
    self.cache = cache

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
  async def countlink(self, context: commands.Context, channel: discord.TextChannel):
    await context.message.delete()
    self.cache.hset(f'counting:{context.guild.id}', key='channelid', value=channel.id)
    await context.send(f'Linked {channel} for counting')
  
  @commands.command(name='countset')
  async def countset(self, context: commands.Context, deci: int = 0, hexa: int = 0, bina: int = 0):
    await context.message.delete()
    self.cache.hset(f'counting:{context.guild.id}', key='Decimal', value=deci)
    self.cache.hset(f'counting:{context.guild.id}', key='Hexadecimal', value=hexa)
    self.cache.hset(f'counting:{context.guild.id}', key='Binary', value=bina)
    await context.send(f'Set values for each team: Decimal: {deci}, Hexadecimal: {hex(hexa)}, Binary: {bin(bina)}')
  
  @commands.command(name='countteamadd')
  async def counteamadd(self, context: commands.Context, name: str, prefix: str, base: int):
    # TODO: Implement dynamic teams not hardcoded
    await context.message.delete()
    await context.send('Command unimplemented!')