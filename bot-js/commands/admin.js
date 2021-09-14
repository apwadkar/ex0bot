const { SlashCommandBuilder } = require('@discordjs/builders');
const { OWNER_ID } = require('../config');
const karma = require('./admin/karma');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('admin')
    .setDescription('Administration commands')
    .addSubcommandGroup(karma.data)
    .setDefaultPermission(false),
  permissions: [
    {
      id: OWNER_ID,
      type: 2, // User permission
      permission: true,
    },
  ],
  async execute(interaction, redisClient) {
    switch (interaction.options.getSubcommandGroup()) {
      case 'karma':
        await karma.execute(interaction, redisClient);
        break;

      case 'vc':
        break;
    }
  },
};
