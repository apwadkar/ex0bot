require('dotenv').config();

module.exports = {
  TOKEN: process.env['DISCORD_TOKEN'],
  CLIENT_ID: process.env['CLIENT_ID'],
  GUILD_ID: process.env['GUILD_ID'],
  OWNER_ID: process.env['OWNER_ID'],
};
