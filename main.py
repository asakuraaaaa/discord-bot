import discord
from discord import app_commands
import json
import os
import time
import audioop_lts as audioop


TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

BOSS_INTERVALS = {
    "VENATUS": 10, "VIORENT": 10, "LADY DALIA": 18, "EGO": 21,
    "ARANEO": 24, "LIVERA": 24, "UNDOMIEL": 24, "AMENTIS": 29,
    "AQULEUS": 29, "BARON": 32, "GARETH": 32, "SHULIAR": 35,
    "LARBA": 35, "CATENA": 35, "TITORE": 37, "METUS": 48,
    "DUPLICAN": 48, "WANNITAS": 48, "SECRETA": 62, "ORDO": 62,
    "ASTA": 62, "SUPORE": 62,
    "CLEMANTIS": 168, "THYMELE": 168, "SAPHIRUS": 168,
    "NEUTRO": 168, "AURAQ": 168, "RODERICK": 168, "MILAVY": 168,
    "RINGOR": 168, "CHAIFLOCK": 168, "BENJI": 168
}

DATA_FILE = "boss_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

boss_data = load_data()

def get_boss_status(name):
    if name not in boss_data:
        return "🟩 Ready"
    respawn = boss_data[name]["respawn"]
    if time.time() >= respawn:
        return "🟩 Ready"
    remaining = respawn - time.time()
    hrs = int(remaining // 3600)
    mins = int((remaining % 3600) // 60)
    return f"🟥 Cooling Down ({hrs}h {mins}m left)"

@tree.command(name="bosslist", description="Show all bosses and their current status")
async def bosslist(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🗡 Boss Respawn Tracker",
        color=0x00B0F4
    )
    embed.set_footer(text="Epoch-based respawn tracker • Updated live")

    # --- DAILY BOSSES ---
    embed.add_field(name="⚔️ Daily Bosses", value="\u200b", inline=False)

    daily_fields = []
    for boss, interval in BOSS_INTERVALS.items():
        if interval < 168:  # daily bosses
            status = get_boss_status(boss)
            daily_fields.append((boss, status))

    # Add fields in groups of 3
    for i in range(0, len(daily_fields), 3):
        group = daily_fields[i:i+3]
        for boss, status in group:
            embed.add_field(name=boss, value=f"{status}", inline=True)
        # Add an empty invisible field if needed to balance layout
        if len(group) < 3:
            for _ in range(3 - len(group)):
                embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="\u200b", value="\u200b", inline=False)

    # --- WEEKLY BOSSES ---
    embed.add_field(name="🕒 Weekly Boss Hunt", value="\u200b", inline=False)

    weekly_fields = []
    for boss, interval in BOSS_INTERVALS.items():
        if interval == 168:  # weekly bosses
            status = get_boss_status(boss)
            weekly_fields.append((boss, status))

    for i in range(0, len(weekly_fields), 3):
        group = weekly_fields[i:i+3]
        for boss, status in group:
            embed.add_field(name=boss, value=f"{status}", inline=True)
        if len(group) < 3:
            for _ in range(3 - len(group)):
                embed.add_field(name="\u200b", value="\u200b", inline=True)

    await interaction.response.send_message(embed=embed)


@tree.command(name="killboss", description="Report a killed boss and start its cooldown timer")
@app_commands.describe(name="Name of the boss killed")
async def killboss(interaction: discord.Interaction, name: str):
    name = name.upper()
    if name not in BOSS_INTERVALS:
        await interaction.response.send_message(f"❌ Boss `{name}` not found.")
        return
    interval = BOSS_INTERVALS[name]
    respawn_time = time.time() + (interval * 3600)
    boss_data[name] = {"killed": int(time.time()), "respawn": int(respawn_time)}
    save_data(boss_data)
    await interaction.response.send_message(
        f"✅ {name} marked as killed.\nRespawns <t:{int(respawn_time)}:R> ({interval} hours)."
    )

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not set in environment variables.")
    else:
        bot.run(TOKEN)
