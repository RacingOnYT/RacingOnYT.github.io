import discord
from discord.ext.commands import has_permissions
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from discord.app_commands import checks
from ro_py.client import Client
from ro_py import Client
from ro_py.utilities.errors import UserDoesNotExistError
from ro_py.client import Client as RoPyClient
import asyncio
import random
import string
import aiohttp
from datetime import datetime, timedelta
import json
import os
from typing import List, Optional
import re
import io
from collections import defaultdict



intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.bans = True
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

roblox_client = Client()

guild_ids = [1255558888884011083]  # Replace with your server ID


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error has been in a slash command: ", e)


@bot.tree.command(name="event", description="Announce a server start up event")
async def event(interaction: discord.Interaction):
    if "Defence Staff" not in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message("You don't have the required role to use this command!", ephemeral=True)
        return

    embed = discord.Embed(title='Server Start Up', description='''
Someone is hosting a server start up right now, use the link down below to join the Military Base.

Link: https://www.roblox.com/games/18334104602/NEW-Fort-Killarney#!/about

React with the checkmark if you are able to attend the server start up.
''', color=discord.Color.yellow())
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1153026855247544433/1258215380686602282/GFX_1.png?ex=668a87a3&is=66893623&hm=f8db62f3d96d1a19e484ee9045dd78f55f8604dd78d1869a6068610c74095fb9&')  # Replace with the URL of the thumbnail image
    message = await interaction.channel.send('@everyone', embed=embed)
    await message.add_reaction('✔️')
    await interaction.response.send_message("Event announced!", ephemeral=True)

@bot.tree.command(name="cmds", description="List of available commands")
async def cmds(interaction: discord.Interaction):
    embed = discord.Embed(title='Commands', description='List of available commands:', color=discord.Color.blue())
    embed.add_field(name='/event', value='Sends a server start up message', inline=False)
    embed.add_field(name='/shutdown', value='Shuts down the bot (only available to the bot owner)', inline=False)
    embed.add_field(name='/clear', value='Deletes a specified number of messages', inline=False)
    embed.add_field(name='/kick', value='Kicks a Player', inline=False)
    embed.add_field(name='/ban', value='Bans a Player', inline=False)
    await interaction.response.send_message(embed=embed)


# Moderation tools
@bot.tree.command(name="mute", description="Temporarily mute a user")
async def mute(interaction: discord.Interaction, user: discord.Member, duration: int):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to mute users.", ephemeral=True)
        return
    await user.timeout(duration=duration, reason="Muted by moderator")
    await interaction.response.send_message(f"Muted {user.mention} for {duration} minutes.")

@bot.tree.command(name="unmute", description="Unmute a user")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to unmute users.", ephemeral=True)
        return
    await user.timeout(duration=None, reason="Unmuted by moderator")
    await interaction.response.send_message(f"Unmuted {user.mention}.")

@bot.tree.command(name="warn", description="Warn a user")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("You don't have permission to warn users.", ephemeral=True)
        return
    await interaction.response.send_message(f"Warned {user.mention} for {reason}.")

@bot.tree.command(name="kick", description="Kick a user from the server")
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permission to kick users.", ephemeral=True)
        return
    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.mention} for {reason}.")

@bot.tree.command(name="ban", description="Ban a user from the server")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("You don't have permission to ban users.", ephemeral=True)
        return
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user.mention} for {reason}.")

#LEVELING SYSTEM ----------------------------------------------------------------

# WIP

#VERIFY COMMANDS!----------------------------------------------------

@bot.tree.command(name="verify", description="Verify your account")
async def verify(interaction: discord.Interaction):
            # Generate a random Captcha code
            captcha_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

            # Send the Captcha code to the user via DM
            embed = discord.Embed(title='Verification', description=f'Please type the following code to verify: `{captcha_code}`', color=discord.Color.blue())
            await interaction.user.send(embed=embed)

            # Notify the user in the interaction channel to check their DMs
            await interaction.response.send_message("Check your DMs for the Verification Code.", ephemeral=True)

            # Wait for the user to respond with the Captcha code
            def check(message):
                return message.author == interaction.user and isinstance(message.channel, discord.DMChannel)

            try:
                response = await bot.wait_for('message', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                embed = discord.Embed(title='Verification Timed Out', description='You took too long to respond. Please try again.', color=discord.Color.red())
                await interaction.user.send(embed=embed)
                return

            # Check if the user's response matches the Captcha code
            if response.content == captcha_code:
                # Verify the user's account and give them a role
                role = discord.utils.get(interaction.guild.roles, name='Verified')
                if role is None:
                    embed = discord.Embed(title='Error', description='Verified role not found.', color=discord.Color.red())
                    await interaction.user.send(embed=embed)
                    return
                await interaction.user.add_roles(role)
                embed = discord.Embed(title='Verification Successful', description='You have been given the Verified role.', color=discord.Color.green())
                await interaction.user.send(embed=embed)
            else:
                embed = discord.Embed(title='Invalid Captcha Code', description='Please try again.', color=discord.Color.red())
                await interaction.user.send(embed=embed)


#USERLOOKUP COMMAND---------------------------------------------------

@bot.tree.command(name="userinfo", description="Get detailed information about a user")
@app_commands.checks.has_permissions(kick_members=True)
async def userinfo(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    # If no user is specified, use the command invoker
    user = user or interaction.user

    # Create the embed
    embed = discord.Embed(title=f'User Information: {user}', color=user.color or discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)

    # Basic info
    embed.add_field(name='ID', value=user.id, inline=True)
    embed.add_field(name='Nickname', value=user.nick or 'None', inline=True)
    embed.add_field(name='Bot', value='Yes' if user.bot else 'No', inline=True)

    # Dates
    embed.add_field(name='Account Created', value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
    embed.add_field(name='Joined Server', value=f"<t:{int(user.joined_at.timestamp())}:R>", inline=True)

    # Roles
    roles = [role.mention for role in reversed(user.roles) if role != interaction.guild.default_role]
    embed.add_field(name=f'Roles [{len(roles)}]', value=' '.join(roles) if roles else 'None', inline=False)

    # Permissions
    key_permissions = ['administrator', 'manage_guild', 'manage_roles', 'manage_channels', 'manage_messages', 'manage_webhooks', 'manage_nicknames', 'manage_emojis', 'kick_members', 'ban_members', 'mention_everyone']
    user_permissions = [perm[0].replace('_', ' ').title() for perm in user.guild_permissions if perm[0] in key_permissions and perm[1]]
    embed.add_field(name='Key Permissions', value=', '.join(user_permissions) if user_permissions else 'None', inline=False)

    # Activity
    if user.activity:
        if isinstance(user.activity, discord.Game):
            embed.add_field(name='Currently Playing', value=user.activity.name, inline=False)
        elif isinstance(user.activity, discord.Streaming):
            embed.add_field(name='Streaming', value=f"[{user.activity.name}]({user.activity.url})", inline=False)
        elif isinstance(user.activity, discord.Spotify):
            embed.add_field(name='Listening to Spotify', value=f"{user.activity.title} by {user.activity.artist}", inline=False)
        elif isinstance(user.activity, discord.CustomActivity):
            embed.add_field(name='Custom Status', value=user.activity.name, inline=False)

    # Server-specific info
    if interaction.guild.owner == user:
        embed.add_field(name='Server Owner', value='Yes', inline=True)
    
    member_count = sorted(interaction.guild.members, key=lambda m: m.joined_at).index(user) + 1
    embed.add_field(name='Join Position', value=f'{member_count}/{len(interaction.guild.members)}', inline=True)

    # Acknowledgements
    acknowledgements = []
    if user.guild_permissions.administrator:
        acknowledgements.append("Server Administrator")
    if user.guild_permissions.manage_guild:
        acknowledgements.append("Server Manager")
    if user.guild_permissions.ban_members:
        acknowledgements.append("Server Moderator")
    if acknowledgements:
        embed.add_field(name='Acknowledgements', value=', '.join(acknowledgements), inline=False)

    # Footer
    embed.set_footer(text=f'Requested by {interaction.user}', icon_url=interaction.user.display_avatar.url)
    embed.timestamp = datetime.utcnow()

    await interaction.response.send_message(embed=embed)

@userinfo.error
async def userinfo_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

#RPSCOMMAND------------------------------------------------------------

@bot.tree.command(name="rps", description="Play Rock, Paper, Scissors with the bot")
async def rps(interaction: discord.Interaction, choice: str):
    # Convert the user's choice to lowercase
    user_choice = choice.lower()

    # Define a list of possible choices
    choices = ['rock', 'paper', 'scissors']

    # Check if the user's choice is valid
    if user_choice not in choices:
        await interaction.response.send_message('Invalid choice. Please choose either rock, paper, or scissors.')
        return

    # Generate a random choice for the bot
    bot_choice = random.choice(choices)

    # Determine the winner
    if user_choice == bot_choice:
        await interaction.response.send_message('It\'s a tie!')
    elif (user_choice == 'rock' and bot_choice == 'scissors') or (user_choice == 'scissors' and bot_choice == 'paper') or (user_choice == 'paper' and bot_choice == 'rock'):
        await interaction.response.send_message(f'{interaction.user.mention} wins!')
    else:
        await interaction.response.send_message(f'Bot wins!')

#ANNOUCEMENT COMMAND

class AnnouncementView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author
        self.reactions = []

    @discord.ui.button(label="👍", style=discord.ButtonStyle.primary)
    async def thumbs_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_reaction(interaction, "👍")

    @discord.ui.button(label="👎", style=discord.ButtonStyle.primary)
    async def thumbs_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_reaction(interaction, "👎")

    @discord.ui.button(label="❓", style=discord.ButtonStyle.primary)
    async def question(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_reaction(interaction, "❓")

    async def handle_reaction(self, interaction: discord.Interaction, emoji: str):
        if interaction.user in self.reactions:
            await interaction.response.send_message("You've already reacted to this announcement.", ephemeral=True)
        else:
            self.reactions.append(interaction.user)
            await interaction.response.send_message(f"You reacted with {emoji}", ephemeral=True)
            await self.update_count(interaction)

    async def update_count(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Reactions: {len(self.reactions)}")
        await interaction.message.edit(embed=embed)

@bot.tree.command(name="announce", description="Send an announcement to the announcements channel")
@app_commands.checks.has_permissions(manage_messages=True)
async def announce(interaction: discord.Interaction, title: str, message: str, channel: Optional[discord.TextChannel] = None, ping_role: Optional[discord.Role] = None, image_url: Optional[str] = None):
    # Get the announcement channel
    if channel is None:
        channel = discord.utils.get(interaction.guild.channels, name='announcements')
    if channel is None:
        await interaction.response.send_message('Announcement channel not found.', ephemeral=True)
        return

    # Create the embed
    embed = discord.Embed(title=title, description=message, color=discord.Color.blue())
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
    embed.timestamp = discord.utils.utcnow()

    if image_url:
        embed.set_image(url=image_url)

    # Create the view with reaction buttons
    view = AnnouncementView(interaction.user)

    # Send the announcement
    content = ping_role.mention if ping_role else None
    announcement_message = await channel.send(content=content, embed=embed, view=view)

    # Add default reactions
    await announcement_message.add_reaction("👍")
    await announcement_message.add_reaction("👎")
    await announcement_message.add_reaction("❓")

    await interaction.response.send_message(f'Announcement sent to {channel.mention}.', ephemeral=True)

@announce.error
async def announce_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

#TICKET SYSTEM---------------------------------------------------------

class TicketView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label='🎟️ Create a Ticket', style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.open_ticket(interaction)

    async def open_ticket(self, interaction: discord.Interaction):
        # Check if user already has an open ticket
        existing_ticket = discord.utils.get(interaction.guild.channels, name=f'ticket-{interaction.user.name.lower()}')
        if existing_ticket:
            await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
            return

        # Create ticket channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        channel = await interaction.guild.create_text_channel(
            f'ticket-{interaction.user.name}',
            category=interaction.channel.category,
            overwrites=overwrites
        )

        # Send initial message in ticket channel
        embed = discord.Embed(title="New Ticket", description=f"Ticket created by {interaction.user.mention}")
        embed.add_field(name="Instructions", value="Please describe your issue. A staff member will be with you shortly.")
        
        ticket_controls = TicketControls(self.bot, interaction.user)
        await channel.send(embed=embed, view=ticket_controls)

        await interaction.response.send_message(f"Ticket created! Please check {channel.mention}", ephemeral=True)

class TicketControls(View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user

    @discord.ui.button(label='Close', style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels or interaction.user == self.user:
            await interaction.response.send_message("Ticket will be closed in 5 seconds...")
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("You don't have permission to close this ticket.", ephemeral=True)

    @discord.ui.button(label='Claim', style=discord.ButtonStyle.success)
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels:
            await interaction.channel.edit(name=f'claimed-{interaction.channel.name}')
            await interaction.response.send_message(f"Ticket claimed by {interaction.user.mention}")
            self.remove_item(button)
            self.add_item(discord.ui.Button(label='Unclaim', style=discord.ButtonStyle.secondary, custom_id='unclaim'))
        else:
            await interaction.response.send_message("You don't have permission to claim this ticket.", ephemeral=True)

    @discord.ui.button(label='Add User', style=discord.ButtonStyle.primary)
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_modal(AddUserModal(self.bot))
        else:
            await interaction.response.send_message("You don't have permission to add users to this ticket.", ephemeral=True)

    @discord.ui.select(
        placeholder="Select ticket priority",
        options=[
            discord.SelectOption(label="Low", description="Low priority ticket"),
            discord.SelectOption(label="Medium", description="Medium priority ticket"),
            discord.SelectOption(label="High", description="High priority ticket"),
        ]
    )
    async def select_priority(self, interaction: discord.Interaction, select: discord.ui.Select):
        # Check if the user has the staff role
        staff_role = discord.utils.get(interaction.guild.roles, name="staff")  # Replace "Staff" with your actual staff role name
        if staff_role in interaction.user.roles:
            await interaction.channel.edit(name=f'{select.values[0].lower()}-{interaction.channel.name}')
            await interaction.response.send_message(f"Ticket priority set to {select.values[0]}")
        else:
            await interaction.response.send_message("You don't have permission to set the ticket priority.", ephemeral=True)

class AddUserModal(discord.ui.Modal, title='Add User to Ticket'):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    username = discord.ui.TextInput(label='Username', placeholder='Enter the username to add...')

    async def on_submit(self, interaction: discord.Interaction):
        user = discord.utils.get(interaction.guild.members, name=self.username.value)
        if user:
            await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
            await interaction.response.send_message(f"{user.mention} has been added to the ticket.")
        else:
            await interaction.response.send_message("User not found.", ephemeral=True)

@bot.tree.command(name="ticket_setup", description="Set up the ticket system")
@commands.has_permissions(administrator=True)
async def ticket_setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="British Army Support",
        description="Click on the button below if you wish to talk to the support team. They will respond to your request.",
        color=discord.Color.blue()
    )
    view = TicketView(bot)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("Ticket system set up successfully!", ephemeral=True)

# END OF TICKET SYSTEM---------------------------------------------------------

verification_codes = {}

# Define the blacklist of group IDs and the required group ID
BLACKLISTED_GROUPS = {
    32490961: "Group Name 1",
    32006412: "Group Name 2",
    # Add more group IDs and names as needed
}

REQUIRED_GROUP_ID = 32515029  # Replace with the actual ID of the required group

class GroupInfo:
    def __init__(self, name: str, id: int, role: str):
        self.name = name
        self.id = id
        self.role = role

async def fetch_roblox_user(session: aiohttp.ClientSession, username: str) -> Optional[dict]:
    user_id_url = f"https://users.roblox.com/v1/users/search?keyword={username}&limit=10"
    async with session.get(user_id_url) as response:
        if response.status != 200:
            print(f"Error fetching user data: Status {response.status}")
            return None
        data = await response.json()
        if not data['data']:
            print(f"No user found for username: {username}")
            return None
        return data['data'][0]

async def fetch_user_groups(session: aiohttp.ClientSession, user_id: int) -> List[GroupInfo]:
    groups_url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    async with session.get(groups_url) as response:
        if response.status != 200:
            return []
        groups_data = await response.json()
        return [
            GroupInfo(group['group']['name'], group['group']['id'], group['role']['name'])
            for group in groups_data['data']
        ]

async def fetch_user_badges(session: aiohttp.ClientSession, user_id: int) -> List[dict]:
    badges_url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Asc"
    async with session.get(badges_url) as response:
        if response.status != 200:
            return []
        badges_data = await response.json()
        return badges_data.get('data', [])

async def fetch_user_friends(session: aiohttp.ClientSession, user_id: int) -> List[str]:
    friends_url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
    async with session.get(friends_url) as response:
        if response.status != 200:
            return []
        friends_data = await response.json()
        return [friend['name'] for friend in friends_data.get('data', [])]

async def fetch_user_profile(session: aiohttp.ClientSession, user_id: int) -> Optional[dict]:
    profile_url = f"https://users.roblox.com/v1/users/{user_id}"
    async with session.get(profile_url) as response:
        if response.status != 200:
            return None
        return await response.json()

@bot.tree.command(name="background", description="Check a Roblox player's group memberships, badges, friends, and profile description.")
@app_commands.checks.has_role("Command Staff")
async def background(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    print(f"Background check requested for username: {username}")

    async with aiohttp.ClientSession() as session:
        user_data = await fetch_roblox_user(session, username)
        if not user_data:
            print(f"No user data returned for username: {username}")
            await interaction.followup.send(f"No Roblox user found with the username `{username}`. Please check the spelling and try again.", ephemeral=True)
            return

        print(f"User data found: {user_data}")
        user_id = user_data['id']
        display_name = user_data['displayName']

        groups, badges, friends, profile = await asyncio.gather(
            fetch_user_groups(session, user_id),
            fetch_user_badges(session, user_id),
            fetch_user_friends(session, user_id),
            fetch_user_profile(session, user_id)
        )

    blacklisted_groups = [group for group in groups if group.id in BLACKLISTED_GROUPS]
    other_groups = [group for group in groups if group.id not in BLACKLISTED_GROUPS]

    # Check if the user who ran the command is in the required group
    user_in_required_group = any(group.id == REQUIRED_GROUP_ID for group in groups)

    embed = discord.Embed(title=f"Background Check for {username}", color=discord.Color.blue())
    embed.set_thumbnail(url=f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=420&height=420&format=png")
    embed.add_field(name="Display Name", value=display_name, inline=False)
    embed.add_field(name="User ID", value=user_id, inline=False)

    if profile and 'description' in profile:
        description = profile['description'].strip()
        embed.add_field(name="Profile Description", value=description if description else "No description", inline=False)

    # Add the category for blacklisted groups
    if blacklisted_groups:
        embed.add_field(name="⚠️ Blacklisted Groups", value="\n".join([f"**{group.name}** - {group.role}" for group in blacklisted_groups]), inline=False)
        embed.color = discord.Color.red()
    else:
        embed.add_field(name="Blacklisted Groups", value="None", inline=False)

    # Add the category for other groups
    if other_groups:
        embed.add_field(name="Other Groups", value="\n".join([f"**{group.name}** - {group.role}" for group in other_groups[:5]]), inline=False)
        if len(other_groups) > 5:
            embed.add_field(name="", value=f"*and {len(other_groups) - 5} more...*", inline=False)

    # Add the category for the required group
    if user_in_required_group:
        embed.add_field(name="✅ Required Group Status", value="User is in the required group.", inline=False)
    else:
        embed.add_field(name="❌ Required Group Status", value="User is NOT in the required group.", inline=False)

    # Check if the user is cleared
    if not blacklisted_groups and user_in_required_group:
        embed.add_field(name="Status", value="✅ Cleared", inline=False)
    else:
        embed.add_field(name="Status", value="❌ Not Cleared", inline=False)

    if badges:
        recent_badges = sorted(badges, key=lambda x: x.get('awardedDate', ''), reverse=True)[:5]
        embed.add_field(name="Recent Badges", value="\n".join([f"**{badge['name']}** - {badge.get('awardedDate', 'N/A').split('T')[0]}" for badge in recent_badges]), inline=False)
        embed.add_field(name="Total Badges", value=str(len(badges)), inline=False)

    if friends:
        embed.add_field(name="Friends", value="\n".join(friends[:5]), inline=False)
        if len(friends) > 5:
            embed.add_field(name="", value=f"*and {len(friends) - 5} more...*", inline=False)
        embed.add_field(name="Total Friends", value=str(len(friends)), inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)

@background.error
async def background_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingRole):
        if not interaction.response.is_done():
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        else:
            await interaction.followup.send("You don't have permission to use this command.", ephemeral=True)
    else:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
        else:
            await interaction.followup.send(f"An error occurred: {error}", ephemeral=True)

#END OF BACKGROUND CHECK

async def verify_profile(interaction: discord.Interaction, roblox_username: str):
    # Step 1: Get the user's generated verification code
    verification_code = verification_codes.get(interaction.user.id)

    if not verification_code:
        await interaction.response.send_message("Verification failed. No verification code found.", ephemeral=True)
        return

    # Step 2: Use Roblox API to check the user's profile
    profile_url = f"https://users.roblox.com/v1/users/search?keyword={roblox_username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(profile_url) as response:
            if response.status != 200:
                await interaction.response.send_message(f"Failed to retrieve data for `{roblox_username}`.", ephemeral=True)
                return

            data = await response.json()

            # Check if the Roblox username exists
            if len(data['data']) == 0:
                await interaction.response.send_message(f"No Roblox user found with the username `{roblox_username}`.", ephemeral=True)
                return

            user_id = data['data'][0]['id']  # Get the user's Roblox ID

        # Step 3: Get the user's Roblox profile to check the description
        user_profile_url = f"https://users.roblox.com/v1/users/{user_id}"

        async with session.get(user_profile_url) as response:
            if response.status != 200:
                await interaction.response.send_message(f"Failed to retrieve profile for `{roblox_username}`.", ephemeral=True)
                return

            user_data = await response.json()

            # Step 4: Check if the verification code is in the description
            if str(verification_code) in user_data.get('description', ''):
                # Code matches, assign the verified role
                verified_role = discord.utils.get(interaction.guild.roles, name="Verified")
                if verified_role:
                    await interaction.user.add_roles(verified_role)
                    await interaction.response.send_message(f"✅ {interaction.user.mention}, you have been successfully verified!", ephemeral=True)
                else:
                    await interaction.response.send_message("The 'Verified' role does not exist in this server. Please contact an admin.", ephemeral=True)
            else:
                # Code doesn't match
                await interaction.response.send_message(f"Verification failed. Could not find the code in `{roblox_username}`'s profile.", ephemeral=True)

# Slash command for Roblox verification
@bot.tree.command(name="roblox-verify", description="Verify your Roblox account by updating your profile description.")
async def roblox_verify(interaction: discord.Interaction, roblox_username: str):
    # Step 1: Generate a random verification code for the user
    verification_code = random.randint(1000, 9999)
    verification_codes[interaction.user.id] = verification_code

    # Step 2: Ask the user to update their Roblox profile description
    message = (
        f"Please add this verification code `{verification_code}` to your Roblox profile description,"
        " then run the command again."
    )
    await interaction.response.send_message(message, ephemeral=True)

# END OF ROBLOX VERIFICATION

# Dictionary to track actions for each user (you can replace this with a database for long-term storage)
user_actions_log = {}

# Function to log actions to the user_actions_log
def log_action(user_id, action_type, description):
    if user_id not in user_actions_log:
        user_actions_log[user_id] = []
    user_actions_log[user_id].append({
        'type': action_type,
        'description': description,
        'timestamp': datetime.now()
    })

# Event: When a message is sent, log the message
@bot.event
async def on_message(message):
    if not message.author.bot:
        log_action(message.author.id, "message", f"Chatted in #{message.channel.name}: {message.content[:50]}...")
    await bot.process_commands(message)

# Event: When a member is kicked, log the kick
@bot.event
async def on_member_remove(member):
    # This will only log if the member is kicked
    log_action(member.id, "leave", f"Left or was kicked from the server.")

# Event: When a member is banned, log the ban
@bot.event
async def on_member_ban(guild, user):
    log_action(user.id, "ban", f"Banned from the server.")

# Event: When a member joins the server, log the join
@bot.event
async def on_member_join(member):
    log_action(member.id, "join", f"Joined the server.")

# Event: When a member leaves the server, log the leave
@bot.event
async def on_member_remove(member):
    log_action(member.id, "leave", f"Left the server.")

# Event: When a member's roles are updated, log the change
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        if added_roles:
            log_action(after.id, "role_add", f"Added roles: {', '.join(role.name for role in added_roles)}")
        if removed_roles:
            log_action(after.id, "role_remove", f"Removed roles: {', '.join(role.name for role in removed_roles)}")

# Slash command to view a user's actions
@bot.tree.command(name="action-view", description="View a user's detailed actions in the server.")
@app_commands.checks.has_permissions(kick_members=True)
async def action_view(interaction: discord.Interaction, user: discord.Member, timeframe: str = None):
    # Check if the command user has the necessary permissions
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Create an embed with the user's information
    embed = discord.Embed(title=f"User Actions for {user.display_name}", color=user.color or discord.Color.blue())
    embed.set_thumbnail(url=user.display_avatar.url)

    # Add relevant user information
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    
    roles = ", ".join([role.mention for role in user.roles if role.name != "@everyone"])
    embed.add_field(name="Roles", value=roles if roles else "No roles", inline=False)

    # Fetch the user's actions from the log
    all_actions = user_actions_log.get(user.id, [])
    
    # Filter actions based on timeframe
    if timeframe:
        if timeframe == "day":
            cutoff = datetime.now() - timedelta(days=1)
        elif timeframe == "week":
            cutoff = datetime.now() - timedelta(weeks=1)
        elif timeframe == "month":
            cutoff = datetime.now() - timedelta(days=30)
        actions = [action for action in all_actions if action['timestamp'] > cutoff]
    else:
        actions = all_actions

    if actions:
        # Group actions by type
        action_groups = {}
        for action in actions:
            action_type = action['type']
            if action_type not in action_groups:
                action_groups[action_type] = []
            action_groups[action_type].append(action)

        # Add grouped actions to the embed
        for action_type, group in action_groups.items():
            action_text = "\n".join([f"- {action['description']} ({action['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})" for action in group[:5]])
            if len(group) > 5:
                action_text += f"\n... and {len(group) - 5} more"
            embed.add_field(name=f"{action_type.capitalize()} Actions", value=action_text, inline=False)

        # Add summary statistics
        total_actions = len(actions)
        embed.add_field(name="Total Actions", value=total_actions, inline=True)
        if total_actions > 0:
            most_common_action = max(action_groups, key=lambda x: len(action_groups[x]))
            embed.add_field(name="Most Common Action", value=most_common_action.capitalize(), inline=True)
    else:
        embed.add_field(name="Actions", value="No actions recorded for the specified timeframe.", inline=False)

    # Add footer with timestamp
    embed.set_footer(text=f"Requested by {interaction.user.display_name} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

    # Send the embed as an ephemeral message
    await interaction.response.send_message(embed=embed, ephemeral=True)

@action_view.autocomplete('timeframe')
async def timeframe_autocomplete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name='Last 24 hours', value='day'),
        app_commands.Choice(name='Last 7 days', value='week'),
        app_commands.Choice(name='Last 30 days', value='month'),
   ]
    return choices

# START OF AUTOMOD

# Constants for automod
MAX_MENTIONS = 5
MAX_LINKS = 3
SPAM_THRESHOLD = 5
SPAM_INTERVAL = 5  # seconds
BANNED_WORDS = ['nigga', 'nigger', 'fuck']  # Add your own banned words

# Tracking dictionaries
user_message_count = defaultdict(list)
warned_users = defaultdict(int)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    # Check for excessive mentions
    if len(message.mentions) > MAX_MENTIONS:
        await message.delete()
        await message.channel.send(f"{message.author.mention}, please don't mention too many users at once.")
        return

    # Check for excessive links
    if len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\)]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)) > MAX_LINKS:
        await message.delete()
        await message.channel.send(f"{message.author.mention}, please don't post too many links at once.")
        return

    # Check for banned words
    if any(word in message.content.lower() for word in BANNED_WORDS):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, your message contained banned words and was deleted.")
        return

    # Check for spam
    current_time = datetime.now()
    user_message_count[message.author.id] = [msg_time for msg_time in user_message_count[message.author.id] if current_time - msg_time < timedelta(seconds=SPAM_INTERVAL)]
    user_message_count[message.author.id].append(current_time)
    
    if len(user_message_count[message.author.id]) > SPAM_THRESHOLD:
        warned_users[message.author.id] += 1
        await message.channel.send(f"{message.author.mention}, please slow down. You're sending messages too quickly.")
        
        if warned_users[message.author.id] >= 3:
            try:
                await message.author.timeout(timedelta(minutes=5), reason="Excessive spamming")
                await message.channel.send(f"{message.author.mention} has been timed out for 5 minutes due to excessive spamming.")
            except discord.errors.Forbidden:
                await message.channel.send(f"I don't have permission to timeout {message.author.mention}.")
        return

@bot.tree.command(name="set_automod", description="Configure automod settings")
@app_commands.checks.has_permissions(manage_guild=True)
async def set_automod(interaction: discord.Interaction, max_mentions: int = None, max_links: int = None, spam_threshold: int = None, spam_interval: int = None):
    global MAX_MENTIONS, MAX_LINKS, SPAM_THRESHOLD, SPAM_INTERVAL

    if max_mentions is not None:
        MAX_MENTIONS = max_mentions
    if max_links is not None:
        MAX_LINKS = max_links
    if spam_threshold is not None:
        SPAM_THRESHOLD = spam_threshold
    if spam_interval is not None:
        SPAM_INTERVAL = spam_interval

    await interaction.response.send_message(f"Automod settings updated:\nMax Mentions: {MAX_MENTIONS}\nMax Links: {MAX_LINKS}\nSpam Threshold: {SPAM_THRESHOLD}\nSpam Interval: {SPAM_INTERVAL} seconds", ephemeral=True)

@bot.tree.command(name="add_banned_word", description="Add a word to the banned words list")
@app_commands.checks.has_permissions(manage_guild=True)
async def add_banned_word(interaction: discord.Interaction, word: str):
    global BANNED_WORDS
    BANNED_WORDS.append(word.lower())
    await interaction.response.send_message(f"Added '{word}' to the banned words list.", ephemeral=True)

@bot.tree.command(name="remove_banned_word", description="Remove a word from the banned words list")
@app_commands.checks.has_permissions(manage_guild=True)
async def remove_banned_word(interaction: discord.Interaction, word: str):
    global BANNED_WORDS
    if word.lower() in BANNED_WORDS:
        BANNED_WORDS.remove(word.lower())
        await interaction.response.send_message(f"Removed '{word}' from the banned words list.", ephemeral=True)
    else:
        await interaction.response.send_message(f"'{word}' is not in the banned words list.", ephemeral=True)

#END OF AUTOMOD

#START OF CLOCKING SYSTEM

#WIP

# END OF CLOCKING SYSTEM

@bot.event
async def on_ready():
    activity = discord.Game(name="Ghostinz USAF!")  # Change the name to whatever you want
    await bot.change_presence(activity=activity)
    print(f'{bot.user} has connected to Discord!')
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error occurred while syncing commands:", e)

OWNER_ID = 781891266295627786  # Replace with your UserID

@bot.command(name="shutdown", help="Shut down the bot")
@commands.has_permissions(administrator=True)  # Ensure only admins can use this command
async def shutdown(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("You don't have permission to shut down the bot.")
        return

    await ctx.send('Shutting down...')
    await bot.close()






bot.run(os.getenv("DISCORD_TOKEN")) # Replace with your actual bot token
