import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os  # ✅ FIX 1

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# CONFIG
# ==========================================
OWNER_ID = 923096413934616596  # 🔥 replace with your real Discord ID

SUPPORT_CATEGORY_ID = 1466995318246609069
REPORT_CATEGORY_ID = 1491264107364745216
BUY_CATEGORY_ID = 1491264209969872997
ADMINSHIP_CATEGORY_ID = 1491264151786360855

# ==========================================
# BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# STORAGE
# ==========================================
active_tickets = {}
ticket_counter = 0

# ==========================================
# CLOSE CONFIRMATION (PUBLIC)
# ==========================================
class ConfirmCloseView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=30)
        self.channel = channel

    @discord.ui.button(label="✅ Confirm Close", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "🔒 Closing ticket...",
            ephemeral=True
        )

        await self.channel.delete()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "❌ Cancelled.",
            ephemeral=True
        )

# ==========================================
# CLOSE BUTTON
# ==========================================
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "⚠️ Are you sure you want to close this ticket?",
            view=ConfirmCloseView(interaction.channel),
            ephemeral=True
        )

# ==========================================
# TICKET SYSTEM
# ==========================================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction, category_id, prefix, message):
        global ticket_counter

        user_id = interaction.user.id
        guild = interaction.guild
        category = guild.get_channel(category_id)

        # ❌ prevent duplicate ticket
        if user_id in active_tickets:
            ch = guild.get_channel(active_tickets[user_id])
            if ch:
                return await interaction.response.send_message(
                    f"❌ You already have a ticket: {ch.mention}",
                    ephemeral=True
                )

        # 🔢 ticket number
        ticket_counter += 1
        ticket_number = str(ticket_counter).zfill(3)

        # 🔐 permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # 📁 create channel
        channel = await guild.create_text_channel(
            name=f"{prefix}-{ticket_number}",
            category=category,
            overwrites=overwrites
        )

        active_tickets[user_id] = channel.id

        # 📩 send ticket message
        await channel.send(
            f"{interaction.user.mention}\n{message}\n\n🎫 Ticket #{ticket_number}",
            view=CloseView()
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

    # ==========================================
    # BUTTONS
    # ==========================================
    @discord.ui.button(label="💰 Buy", style=discord.ButtonStyle.green)
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction,
            BUY_CATEGORY_ID,
            "buy",
            "💰 Buy ticket created. Staff will assist you."
        )

    @discord.ui.button(label="🚨 Report", style=discord.ButtonStyle.red)
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction,
            REPORT_CATEGORY_ID,
            "report",
            "🚨 Report ticket created. Please explain your issue."
        )

    @discord.ui.button(label="💼 Adminship", style=discord.ButtonStyle.blurple)
    async def adminship(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(
            interaction,
            ADMINSHIP_CATEGORY_ID,
            "adminship",
            "💼 Adminship application ticket created."
        )

# ==========================================
# COMMAND: SEND PANEL (PUBLIC)
# ==========================================
@bot.tree.command(name="ticket_panel", description="Send ticket panel")
async def ticket_panel(interaction: discord.Interaction):

    # 👑 OWNER ONLY ACCESS
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message(
            "❌ You are not allowed to use this command.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🎫 SUPPORT CENTER",
        description=(
            "Click a button below to create a ticket:\n\n"
            "💼 Adminship – Apply for admin\n"
            "💰 Buy – Purchase help\n"
            "🚨 Report – Private report"
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

# ==========================================
# READY EVENT
# ==========================================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} commands")
    except Exception as e:
        print(e)


# ==========================================
# RUN BOT
# ==========================================
keep_alive()
bot.run(TOKEN)
