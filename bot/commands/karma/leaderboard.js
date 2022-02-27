const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');
const { MessageEmbed } = require('discord.js');

const karmaKey = (guild_id) => `karma:${guild_id}`;

const karmasToStr = (interaction) => async (value) =>
  `${await interaction.guild.members.fetch(value.key)}: ${value.value}`;

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('leaderboard')
    .setDescription("Current leaderboard for this server's karma"),
  async execute(interaction, redisClient) {
    const getall = await redisClient.hGetAll(karmaKey(interaction.guildId));
    const karmas = [];
    for (const key in getall) {
      karmas.push({ key, value: Number(getall[key]) });
    }
    const reverse = await Promise.all(
      karmas
        .sort((a, b) => a.value - b.value)
        .slice(0, 10)
        .map(karmasToStr(interaction))
    );
    const sorted = await Promise.all(
      karmas
        .sort((a, b) => b.value - a.value)
        .slice(0, 10)
        .map(karmasToStr(interaction))
    );

    const embed = new MessageEmbed()
      .setTitle(`Leaderboard for ${interaction.guild}`)
      .setThumbnail(interaction.guild.iconURL())
      .setAuthor(
        interaction.member.displayName,
        interaction.member.user.displayAvatarURL()
      )
      .addField('Top 10', sorted.join('\n'))
      .addField('Bottom 10', reverse.join('\n'));

    await interaction.reply({ embeds: [embed] });
  },
};
