const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');
const { KARMA_KEY } = require('../../../utils');

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('emojis')
    .setDescription('Set emojis for karma tracking')
    .addStringOption((input) =>
      input
        .setName('negative')
        .setDescription('Negative valued emoji')
        .setRequired(true)
    )
    .addStringOption((input) =>
      input
        .setName('positive')
        .setDescription('Positive valued emoji')
        .setRequired(true)
    ),
  async execute(interaction, redisClient) {
    const positive = interaction.options.getString('positive');
    const negative = interaction.options.getString('negative');
    await redisClient.sAdd(
      `${KARMA_KEY(interaction.guildId)}:positive`,
      positive
    );
    await redisClient.sAdd(
      `${KARMA_KEY(interaction.guildId)}:negative`,
      negative
    );
    await interaction.reply({
      content: `Set emojis (+1: ${positive}, -1: ${negative}) for karma tracking`,
      ephemeral: true,
    });
  },
};
