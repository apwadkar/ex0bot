const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');
const { KARMA_KEY } = require('../../../utils');

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('link')
    .setDescription('Link a channel for karma tracking')
    .addChannelOption((input) =>
      input
        .setName('channel')
        .setDescription('Channel to link')
        .setRequired(true)
    ),
  async execute(interaction, redisClient) {
    const channel = interaction.options.getChannel('channel');
    await redisClient.sAdd(
      `${KARMA_KEY(interaction.guildId)}:channels`,
      channel.id
    );
    await interaction.reply({
      content: `Linked ${channel} for karma tracking`,
      ephemeral: true,
    });
  },
};
