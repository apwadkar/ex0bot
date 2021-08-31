const { TOKEN, CLIENT_ID, GUILD_ID } = require('../config');

const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');

const commands = [new SlashCommandBuilder().setName('ping').setDescription('Replies with pong')].map((command) => command.toJSON());

const rest = new REST({ version: '9' }).setToken(TOKEN);

(async () => {
  try {
    await rest.put(Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID), { body: commands });

    console.log('Successfully registered application commands.');
  } catch (error) {
    console.error(error);
  }
})();
