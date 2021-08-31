const { TOKEN } = require('./config');

const { Client, Intents } = require('discord.js');
const client = new Client({
  intents: [Intents.FLAGS.GUILD_MEMBERS],
});

client.once('ready', () => {
  console.log('Ready!');
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isCommand()) return;

  const { commandName } = interaction;

  if (commandName === 'ping') {
    await interaction.reply('Pong');
  }
});

client.login(TOKEN);
