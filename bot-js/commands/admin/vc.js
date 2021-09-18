const { SlashCommandSubcommandGroupBuilder } = require('@discordjs/builders');
const link = require('./vc/link');
const unlink = require('./vc/unlink');

module.exports = {
  data: new SlashCommandSubcommandGroupBuilder()
    .setName('vc')
    .setDescription('Temporary voice channel administration commands')
    .addSubcommand(link.data)
    .addSubcommand(unlink.data),
  async execute(interaction, redisClient) {
    switch (interaction.options.getSubcommand()) {
      case 'link':
        await link.execute(interaction, redisClient);
        break;

      case 'unlink':
        await unlink.execute(interaction, redisClient);
        break;
    }
  },
};
