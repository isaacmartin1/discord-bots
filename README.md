# discord-bots
Why talk to your friends when you can talk to a bot?

Commands:
- `summon` - bring the bot into your current voice chat
- `banish` - remove the bot from any channel its in
- `roll` - roll a value for your friends
- `mimic` - have the bot mimic one of your friends

## Technical Details
Create a .env with the value `TOKEN`, containing your discord bot token. This is meant to be run locally. In this case, the default is a version of llama.

Change the `config.example.yaml` to `config.yaml`.

Run `make start` to run the bot and `make install` to install packages for the bot.
