const { Permissions } = require('discord.js');

module.exports = {
  name: 'voiceStateUpdate',
  async execute(oldState, newState) {
    const client = oldState.guild.client;
    const redisClient = client.redisClient;

    const beforeChannel = oldState.channel;
    const afterChannel = newState.channel;
    if (
      beforeChannel &&
      beforeChannel !== afterChannel &&
      (await redisClient.get(`tempchannel:${beforeChannel.id}`))
    ) {
      if (beforeChannel.members.size === 0) {
        await redisClient.del(`tempchannel:${beforeChannel.id}`);
        await beforeChannel.delete('No more users left in channel');
      }
    }

    if (afterChannel && (await redisClient.get(`channel:${afterChannel.id}`))) {
      const parent = afterChannel.parent;
      const permissionOverwrites = [
        {
          id: newState.member.id,
          allow: [
            Permissions.FLAGS.MANAGE_CHANNELS,
            Permissions.FLAGS.MANAGE_ROLES,
            Permissions.FLAGS.VIEW_CHANNEL,
          ],
          type: 'member',
        },
      ];
      const channel = await newState.guild.channels.create('Temp VC', {
        type: 'GUILD_VOICE',
        parent,
        reason: `Temporary channel requested by ${newState.member.displayName}`,
        permissionOverwrites,
      });
      newState.setChannel(channel, 'Moving to new temporary channel');
      await redisClient.set(`tempchannel:${channel.id}`, '1');
    }
  },
};
