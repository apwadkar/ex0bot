const { SlashCommandSubcommandGroupBuilder } = require('@discordjs/builders');
const emojis = require('./karma/emojis');
const link = require('./karma/link');
const unlink = require('./karma/unlink');

module.exports = {
  data: new SlashCommandSubcommandGroupBuilder()
    .setName('karma')
    .setDescription('Administration for karma commands')
    .addSubcommand(link.data)
    .addSubcommand(unlink.data)
    .addSubcommand(emojis.data),
  async execute(interaction, redisClient) {
    switch (interaction.options.getSubcommand()) {
      case 'link':
        await link.execute(interaction, redisClient);
        break;

      case 'unlink':
        await unlink.execute(interaction, redisClient);
        break;

      case 'emojis':
        await emojis.execute(interaction, redisClient);
        break;
    }
  },
};
