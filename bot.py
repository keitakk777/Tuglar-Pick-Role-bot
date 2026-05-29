import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import os

# === TRÁI TIM NHÂN TẠO (GIỮ BOT SỐNG TRÊN RENDER) ===
app = Flask('')

@app.route('/')
def home():
    return "Bot Tuglar đang sống nhăn răng trên Render!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()
# ====================================================

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ================= CẤU HÌNH =================
# Dùng biến môi trường để giấu Token an toàn trên Render
TOKEN = os.environ.get('DISCORD_TOKEN') 

SERVER_ID = 123456789012345678 # BẮT BUỘC: Thay bằng ID Server Discord của bạn
BOOSTER_ROLE_ID = 1000062456007249930 # ID role Server Booster gốc

# Cấu hình Cấp bậc Booster (Mốc Số Ngày : ID Role Tương Ứng)
BOOSTER_TIERS = {
    7: 1509967931675640039,  # Thay bằng ID Role Booster I
    14: 1509970643993628672, # Thay bằng ID Role Booster II
    21: 1509970708850020523, # Thay bằng ID Role Booster III
    28: 1509970736767438879, # Thay bằng ID Role Booster IV
    35: 1509970770305224918, # Thay bằng ID Role Booster V
    42: 1509970819932094584, # Thay bằng ID Role Booster VI
    49: 1509970853192798259, # Thay bằng ID Role Booster VII
    56: 1509962710928982288  # Thay bằng ID Role Booster VIII
}

MESSAGE_CONFIGS = {
    # ------ BẢNG 1: CHỌN MÀU ------
    1507323471984722030: { 
        "type": "Màu",
        "mapping": {
            "1️⃣": 1162545019123666984,
            "2️⃣": 1157298054764974130,
            "3️⃣": 1157296480722366555,
            "4️⃣": 1157297666879926304,
            "5️⃣": 1157298499461840906 
        }
    },
    
    # ------ BẢNG 2: CHỌN ICON ------
    1507323572824309780: { 
        "type": "Icon",
        "mapping": {
            "1️⃣": 1164764867769667664,
            "2️⃣": 1164766440335876126,
            "3️⃣": 1164946156858650635,
            "4️⃣": 1164946570920337538 
        }
    }
}
# ============================================

# --- 1. VÒNG LẶP TIẾN HÓA & DỌN DẸP ROLE ĐỊNH KỲ ---
@tasks.loop(hours=24)
async def check_booster_level():
    guild = bot.get_guild(SERVER_ID)
    if not guild: return
    
    now = discord.utils.utcnow()
    all_tier_roles = list(BOOSTER_TIERS.values())
    
    for member in guild.members:
        if member.premium_since:
            days_boosted = (now - member.premium_since).days
            highest_role_id = None
            
            for req_days in sorted(BOOSTER_TIERS.keys(), reverse=True):
                if days_boosted >= req_days:
                    highest_role_id = BOOSTER_TIERS[req_days]
                    break
                    
            if highest_role_id:
                roles_to_add = []
                roles_to_remove = []
                
                target_role = guild.get_role(highest_role_id)
                if target_role and target_role not in member.roles:
                    roles_to_add.append(target_role)
                    
                for r_id in all_tier_roles:
                    if r_id != highest_role_id:
                        old_role = guild.get_role(r_id)
                        if old_role and old_role in member.roles:
                            roles_to_remove.append(old_role)
                            
                if roles_to_add:
                    await member.add_roles(*roles_to_add)
                    print(f"✨ Tiến hóa: [{member.name}] đạt mốc Boost {days_boosted} ngày -> {target_role.name}")
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)
        else:
            roles_to_remove = [guild.get_role(r_id) for r_id in all_tier_roles if guild.get_role(r_id) and guild.get_role(r_id) in member.roles]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)

# --- 2. HỆ THỐNG BÁO ĐỘNG REAL-TIME KHI HỦY BOOST ---
@bot.event
async def on_member_update(before, after):
    if before.premium_since is not None and after.premium_since is None:
        all_tier_roles = list(BOOSTER_TIERS.values())
        roles_to_remove = []
        
        for r_id in all_tier_roles:
            r = after.guild.get_role(r_id)
            if r and r in after.roles:
                roles_to_remove.append(r)
        
        if roles_to_remove:
            await after.remove_roles(*roles_to_remove)
            print(f"💔 [{after.name}] đã ngừng Boost. Thu hồi ngay lập tức toàn bộ role cấp bậc.")

# --- 3. CÁC TÍNH NĂNG PICK ROLE ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã sẵn sàng phục vụ server!')
    if not check_booster_level.is_running():
        check_booster_level.start()
        print('⏳ Hệ thống auto Tiến Hóa Booster đã được kích hoạt!')
    print('-------------------------------------------')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    if payload.message_id in MESSAGE_CONFIGS:
        guild = bot.get_guild(payload.guild_id)
        member = payload.member
        config = MESSAGE_CONFIGS[payload.message_id]
        role_mapping = config["mapping"]
        role_type = config["type"]

        has_booster = any(role.id == BOOSTER_ROLE_ID for role in member.roles)

        if has_booster:
            emoji_name = payload.emoji.name
            if emoji_name in role_mapping:
                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)

                roles_to_remove = []
                for mapped_emoji, mapped_role_id in role_mapping.items():
                    if mapped_emoji != emoji_name: 
                        try:
                            await message.remove_reaction(mapped_emoji, member)
                        except Exception:
                            pass
                            
                        old_role = guild.get_role(mapped_role_id)
                        if old_role and old_role in member.roles:
                            roles_to_remove.append(old_role)
                
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)

                role_id = role_mapping[emoji_name]
                new_role = guild.get_role(role_id)
                if new_role:
                    await member.add_roles(new_role)
        else:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)
            try:
                await member.send("❌ Bạn cần là **Server Booster** để chọn các role đặc biệt này nhé!")
            except discord.Forbidden:
                pass

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in MESSAGE_CONFIGS:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        config = MESSAGE_CONFIGS[payload.message_id]
        role_mapping = config["mapping"]
        emoji_name = payload.emoji.name

        if emoji_name in role_mapping:
            role_id = role_mapping[emoji_name]
            role = guild.get_role(role_id)
            if role and role in member.roles:
                await member.remove_roles(role)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try:
        msg_mau = await ctx.channel.fetch_message(1507323471984722030)
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
            await msg_mau.add_reaction(emoji)
    except Exception:
        pass

    try:
        msg_icon = await ctx.channel.fetch_message(1507323572824309780)
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]:
            await msg_icon.add_reaction(emoji)
    except Exception:
        pass
    
    await ctx.send("✅ Đã setup xong các nút thả tim!", delete_after=5)

# === GỌI LỆNH CHẠY ===
keep_alive() 
bot.run(TOKEN)