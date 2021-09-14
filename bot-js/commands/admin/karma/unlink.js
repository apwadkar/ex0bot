const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');
const { KARMA_KEY } = require('../../../utils');

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('unlink')
    .setDescription('Unlink a channel from karma tracking')
    .addChannelOption((input) =>
      input
        .setName('channel')
        .setDescription('Channel to unlink')
        .setRequired(true)
    ),
  async execute(interaction, redisClient) {
    const channel = interaction.options.getChannel('channel');
    await redisClient.sRem(
      `${KARMA_KEY(interaction.guildId)}:channels`,
      channel.id
    );
    await interaction.reply({
      content: `Unlinked ${channel} from karma tracking`,
      ephemeral: true,
    });
  },
};
