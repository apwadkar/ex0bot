const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('unlink')
    .setDescription('Unlink a staging channel for temporary channels')
    .addChannelOption((input) =>
      input
        .setName('channel')
        .setDescription('Channel to unlink')
        .setRequired(true)
    ),
  async execute(interaction, redisClient) {
    const channel = interaction.options.getChannel('channel');
    if (channel.isVoice()) {
      await redisClient.del(`channel:${channel.id}`);
      await interaction.reply({
        content: `${channel} has been unlinked`,
        ephemeral: true,
      });
    } else {
      await interaction.reply({
        content: `${channel} must be a voice channel`,
        ephemeral: true,
      });
    }
  },
};
