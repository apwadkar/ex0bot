const { SlashCommandBuilder } = require('@discordjs/builders');
const { Permissions } = require('discord.js');
const redis = require('../redis');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('vc')
    .setDescription('Voice Channel')
    .addSubcommand((input) =>
      input
        .setName('new')
        .setDescription('Create a new temporary voice channel')
        .addStringOption((input) =>
          input
            .setName('name')
            .setDescription('Name of the voice channel')
            .setRequired(true)
        )
        .addIntegerOption((input) =>
          input
            .setName('limit')
            .setDescription('Limit of people in the voice channel')
            .setRequired(false)
        )
        .addRoleOption((input) =>
          input
            .setName('restriction')
            .setDescription('Restrict (by role) who can see the voice channel')
            .setRequired(false)
        )
    ),
  permissions: [],
  async execute(interaction, redisClient) {
    if (interaction.options.getSubcommand() === 'new') {
      // Check if user is in a voice channel
      if (interaction.member.voice.channel) {
        const parent = interaction.member.voice.channel.parent;
        const permissionOverwrites = [
          {
            id: interaction.member.id,
            allow: [
              Permissions.FLAGS.MANAGE_CHANNELS,
              Permissions.FLAGS.MANAGE_ROLES,
              Permissions.FLAGS.VIEW_CHANNEL,
            ],
            type: 'member',
          },
        ];
        if (interaction.options.getRole('restriction')) {
          permissionOverwrites.push({
            id: interaction.options.getRole('restriction').id,
            type: 'role',
            allow: Permissions.FLAGS.VIEW_CHANNEL,
          });
          permissionOverwrites.push({
            id: interaction.guild.roles.everyone.id,
            deny: Permissions.FLAGS.VIEW_CHANNEL,
            type: 'role',
          });
        }

        const channel = await interaction.guild.channels.create(
          interaction.options.getString('name'),
          {
            type: 'GUILD_VOICE',
            userLimit: interaction.options.getInteger('limit'),
            parent,
            reason: `Temporary channel requested by ${interaction.member.displayName}`,
            permissionOverwrites,
          }
        );
        await redisClient.set(`tempchannel:${channel.id}`, '1');
        await interaction.member.voice.setChannel(
          channel,
          'Moving to new temporary channel'
        );
        await interaction.reply({
          content: 'Temporary channel created. Moving you into it...',
          ephemeral: true,
        });
      } else {
        await interaction.reply({
          content: 'You must be in a voice channel to make a temporary one!',
          ephemeral: true,
        });
      }
    }
  },
};
