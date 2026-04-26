import discord
import os
from dotenv import load_dotenv

from database import message_db
from llm import get_llm_mimicry

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)
message_database = message_db()

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')

@tree.command()
async def mimic(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()
    # refresh data for every channel in server
    for channel in interaction.guild.text_channels:
        await message_database.batch_retrieve_messages(user.id, channel)
        
    messages = message_database.get_messages(user.id)

    if not messages:
        await interaction.followup.send("No messages available for the user")
        return

    # ask llm to interpret messages and send a message responding to the message content
    # if there's not enough content, respond with a characature of what the user may say
    llm_message = get_llm_mimicry(messages)
    print(f'Sent LLM message {llm_message} mimicking {user.display_name}')
    await interaction.followup.send(llm_message)


client.run(token)
