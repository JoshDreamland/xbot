OMGbot
========
A "modular" IRC bot hacked together in Python. It has acreted over the
years, and now offers a wide variety of plugins. This is the bot's only
redeeming quality.

Setup
========
1. Run pyBot.py. It will prompt for first-time setup information.
  * If you're configuring the bot, you're the owner.
    * The owner can potentially receive debug messages from plugins,
      but is otherwise not important.
    * There's no mechanism to change the owner, but it's trivial.
2. Configure privileges and default plugins through the IRC interface.
  * ONLY the owner configured in Step 1 can do this!
  * Use `!elevate` to grant privileges to other users.
    * You must `!load` this command as well before you can use it.
3. Configure commands
  * Use `!load` to install a command by its name.
  * Use `!alias` to provide convenience calls for given parameters.
    * You must `!load alias`.
  * Some plugins require daemons. For instance, !later requires laterd.
  * Use `!autoload` to make a command load by default.
    * Yes, you must `!load autoload` before you can use it.
    * Yes, you may then `!autoload autoload`.
  * Use `!set` to make an alias persist between runs.
    * Guess what you must first do in order to use `!set`.
4. When in doubt, try `!pluginfo`, then bother sirxemic. If he's dead,
   you can try JoshDreamland.
  * No one is qualified to maintain this bot.
