const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('link')
    .setDescription('Link a voice channel for staging')
    .addChannelOption((input) =>
      input
        .setName('channel')
        .setDescription('Channel to link')
        .setRequired(true)
    ),
  async execute(interaction, redisClient) {
    const channel = interaction.options.getChannel('channel');
    if (channel.isVoice()) {
      await redisClient.set(`channel:${channel.id}`, '1');
      await interaction.reply({
        content: `${channel} has been linked`,
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
