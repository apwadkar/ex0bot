const { SlashCommandBuilder } = require('@discordjs/builders');
const { OWNER_ID } = require('../config');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('admin')
    .setDescription('Administration commands')
    .setDefaultPermission(false),
  permissions: [
    {
      id: OWNER_ID,
      type: 2, // User permission
      permission: true,
    },
  ],
  async execute(interaction) {},
};
