import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import yaml

from database import message_db
from llm import get_llm_mimicry

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)
message_database = message_db()
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')

@tree.command(name="mimic", description="Parrots your friend based on chat history")
@app_commands.guild_only()
async def mimic(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()
    # refresh data for every channel in server
    bot_member = interaction.guild.me
    for channel in interaction.guild.text_channels:
        permissions = channel.permissions_for(bot_member)
        if permissions.read_message_history and permissions.read_messages:
            await message_database.batch_retrieve_messages(user.id, channel)
        
    messages = message_database.get_messages(user.id)

    if not messages:
        await interaction.followup.send("No messages available for the user")
        return

    # ask llm to interpret messages and send a message responding to the message content
    # if there's not enough content, respond with a characature of what the user may say
    llm_message = get_llm_mimicry(messages, config["model_name"])
    print(f'Sent LLM message {llm_message} mimicking {user.display_name}')
    await interaction.followup.send(llm_message)

@tree.command(name="summon", description="Joins your voice chat")
@app_commands.guild_only()
async def summon(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)
        else:
            await channel.connect()
        await interaction.response.send_message(f"Joined {channel.name}")
    else:
        await interaction.response.send_message("You aren't in a voice chat")

@tree.command(name="banish", description="Leaves your voice chat")
@app_commands.guild_only()
async def banish(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("I've left the voice chat!")
    else:
        await interaction.response.send_message("I'm not in a voice chat")

@tree.command(name="roll", description="Rolls a dice for the user")
@app_commands.guild_only()
async def roll(interaction: discord.Interaction):
    message = []
    for member in get_voice_users(interaction):
        roll_dist = config["roll_distribution"]
        roll_val = random.randint(roll_dist["min"], roll_dist["max"])
        outcomes = roll_dist["outcomes"]
        for outcome in outcomes:
            min_outcome, max_outcome = [int(x) for x in outcome.split('-')]
            if min_outcome <= roll_val <= max_outcome:
                message.append(f"{member.mention} rolled a {roll_val}: {outcomes[outcome]}")
                break
    if message:
        await interaction.response.send_message("Rolling the dice...")
        await interaction.channel.send("\n".join(message))
    else:
        await interaction.channel.send("The server's voice chats are empty!")

def get_voice_users(ctx):
    members = []
    for channel in ctx.guild.voice_channels:
        if channel.members:
            members += channel.members
    return members

client.run(token)
