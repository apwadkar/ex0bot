const { SlashCommandBuilder } = require('@discordjs/builders');
const leaderboard = require('./karma/leaderboard');
const get = require('./karma/get');
const init = require('./karma/init');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('karma')
    .setDescription('Karma commands')
    .addSubcommand(leaderboard.data)
    .addSubcommand(get.data)
    .addSubcommand(init.data),
  permissions: [],
  async execute(interaction, redisClient) {
    switch (interaction.options.getSubcommand()) {
      case 'leaderboard':
        await leaderboard.execute(interaction, redisClient);
        break;
      case 'get':
        await get.execute(interaction, redisClient);
        break;
      case 'init':
        await init.execute(interaction, redisClient);
        break;
    }
  },
};
