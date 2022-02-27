const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');

const karmaKey = (guild_id) => `karma:${guild_id}`;

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('init')
    .setDescription("Initializes everyone in the server to 0 karma"),
  async execute(interaction, redisClient) {
    await redisClient.DEL(karmaKey(interaction.guildId));
    const members = await interaction.guild.members.list({ limit: 1000 });
    for (const member of members) {
      await redisClient.sendCommand([
        'HSETNX',
        karmaKey(interaction.guildId),
        member.id,
        '0',
      ]);
    }
    await interaction.reply(`${interaction.guild.name} has been initialized!`);
  },
};
