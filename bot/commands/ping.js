const { SlashCommandBuilder } = require('@discordjs/builders');
const { OWNER_ID } = require('../config');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ping')
    .setDescription('Replies with Pong!')
    .setDefaultPermission(false),
  permissions: [
    {
      id: OWNER_ID,
      type: 2, // User permission
      permission: true,
    },
  ],
  async execute(interaction) {
    await interaction.reply('Pong!');
  },
};
