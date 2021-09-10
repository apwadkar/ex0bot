const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('leaderboard')
    .setDescription("Current leaderboard for this server's karma"),
  permissions: [],
  async execute(interaction) {
    await interaction.reply('karma leaderboard');
  },
};
