const { KARMA_KEY } = require('../../utils');

module.exports = {
  async add(messageReaction, user, redisClient) {
    const author = messageReaction.message.author;
    if (author.id !== user.id) {
      const guildId = messageReaction.message.guildId;
      const emoji = `${messageReaction.emoji}`;
      if (
        await redisClient.sIsMember(`${KARMA_KEY(guildId)}:positive`, emoji)
      ) {
        await redisClient.hIncrBy(KARMA_KEY(guildId), author.id, 1);
      } else if (
        await redisClient.sIsMember(`${KARMA_KEY(guildId)}:negative`, emoji)
      ) {
        await redisClient.hIncrBy(KARMA_KEY(guildId), author.id, -1);
      }
    }
  },
  async remove(messageReaction, user, redisClient) {
    const author = messageReaction.message.author;
    if (author.id !== user.id) {
      const guildId = messageReaction.message.guildId;
      const emoji = `${messageReaction.emoji}`;
      if (
        await redisClient.sIsMember(`${KARMA_KEY(guildId)}:positive`, emoji)
      ) {
        await redisClient.hIncrBy(KARMA_KEY(guildId), author.id, -1);
      } else if (
        await redisClient.sIsMember(`${KARMA_KEY(guildId)}:negative`, emoji)
      ) {
        await redisClient.hIncrBy(KARMA_KEY(guildId), author.id, 1);
      }
    }
  },
};
