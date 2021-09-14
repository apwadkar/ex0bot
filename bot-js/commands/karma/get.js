const { SlashCommandSubcommandBuilder } = require('@discordjs/builders');
const { GUILD_ID } = require('../../config');

const karmaKey = (guild_id) => `karma:${guild_id}`;

module.exports = {
  data: new SlashCommandSubcommandBuilder()
    .setName('get')
    .setDescription("Get user's karma")
    .addUserOption((option) =>
      option.setName('user').setDescription('User to check').setRequired(false)
    ),
  async execute(interaction, redisClient) {
    const user = interaction.options.getUser('user') || interaction.user;
    await redisClient.sendCommand([
      'HSETNX',
      karmaKey(interaction.guildId),
      user.id,
      '0',
    ]);
    const userKarma = await redisClient.hGet(karmaKey(GUILD_ID), user.id);
    await interaction.reply(`${user} has ${userKarma} karma`);
  },
};
