require('dotenv').config();

module.exports = {
  REDIS_URL: process.env['REDIS_URL'],
  TOKEN: process.env['DISCORD_TOKEN'],
  CLIENT_ID: process.env['CLIENT_ID'],
  GUILD_ID: process.env['GUILD_ID'],
  OWNER_ID: process.env['OWNER_ID'],
};
