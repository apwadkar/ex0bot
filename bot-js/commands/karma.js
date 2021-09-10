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
  async execute(interaction) {
    if (interaction.options.getSubcommand() === 'leaderboard') {
      await leaderboard.execute(interaction);
    } else if (interaction.options.getSubcommand() === 'get') {
      await get.execute(interaction);
    }
  },
};
