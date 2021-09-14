module.exports = {
  name: 'voiceStateUpdate',
  once: false,
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
  },
};
