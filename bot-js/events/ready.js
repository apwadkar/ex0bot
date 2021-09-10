const { GUILD_ID } = require('../config');

async function setCommandPermissions(client) {
  console.log('Setting command permissions...');
  const commands = await client.guilds.cache.get(GUILD_ID)?.commands.fetch();
  let permissions = [];
  for ([_, clientCommand] of commands) {
    let command = client.commands.get(clientCommand.name);
    if (command.data) {
      if (command.permissions) {
        permissions.push({
          id: clientCommand.id,
          permissions: command.permissions,
        });
      }
    }
  }
  client.guilds.cache.get(GUILD_ID)?.commands.permissions.set({ fullPermissions: permissions });
  console.log('Permissions set: ', JSON.stringify(permissions, null, 2));
}

module.exports = {
  name: 'ready',
  once: true,
  async execute(client) {
    await setCommandPermissions(client);

    console.log(`Logged in as ${client.user.tag}`);
  },
};
