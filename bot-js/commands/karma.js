const { SlashCommandBuilder } = require('@discordjs/builders');
const leaderboard = require('./karma/leaderboard');
const get = require('./karma/get');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('karma')
    .setDescription('Karma commands')
    .addSubcommand(leaderboard.data)
    .addSubcommand(get.data),
  permissions: [],
  async execute(interaction, redisClient) {
    switch (interaction.options.getSubcommand()) {
      case 'leaderboard':
        await leaderboard.execute(interaction, redisClient);
        break;
      case 'get':
        await get.execute(interaction, redisClient);
        break;
    }
  },
};
