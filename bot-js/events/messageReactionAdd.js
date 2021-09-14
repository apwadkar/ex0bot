const { KARMA_KEY } = require('../utils');
const karma = require('./reactions/karma');

module.exports = {
  name: 'messageReactionAdd',
  async execute(messageReaction, user) {
    if (messageReaction.partial) {
      try {
        await messageReaction.fetch();
      } catch (err) {
        console.error('API Error when trying to fetch message reaction');
        return;
      }
    }
    const guild = messageReaction.message.guild;
    const channel = messageReaction.message.channel;
    const redisClient = messageReaction.client.redisClient;
    if (
      await redisClient.SISMEMBER(`${KARMA_KEY(guild.id)}:channels`, channel.id)
    ) {
      await karma.add(messageReaction, user, redisClient);
    }
  },
};
