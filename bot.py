import discord
from discord.ext import commands
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
# CÁCH 1: Dán thẳng Token (Nhớ giữ kho GitHub ở chế độ Private)
TOKEN = 'MTUwNzMxMTk3OTA3OTkyOTkzOA.GPQou0.0vk4vUq1p3pr3KM6q1QzkWiNymZsGvfSzFM17c'

# CÁCH 2: Nếu Public Github, hãy thêm Biến môi trường DISCORD_TOKEN trên Render
# (Xóa dấu # ở dòng dưới và xóa dòng TOKEN = 'bảo mật' ở trên đi)
# TOKEN = os.environ.get('DISCORD_TOKEN') 

BOOSTER_ROLE_ID = 1000062456007249930 # ID role Server Booster

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

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã sẵn sàng phục vụ server!')
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

                # 1. Quét sạch các nút cũ của User trên màn hình + Thu hồi Role
                roles_to_remove = []
                for mapped_emoji, mapped_role_id in role_mapping.items():
                    if mapped_emoji != emoji_name: 
                        
                        # LUÔN LUÔN ép gỡ UI Reaction cũ (Không cần kiểm tra role)
                        try:
                            await message.remove_reaction(mapped_emoji, member)
                        except Exception:
                            pass
                            
                        # Gom các role cũ để thu hồi
                        old_role = guild.get_role(mapped_role_id)
                        if old_role and old_role in member.roles:
                            roles_to_remove.append(old_role)
                
                # Thực hiện thu hồi role trong hệ thống
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)
                    print(f'🔄 Đã gỡ {role_type} cũ và dọn UI của [{member.name}]')

                # 2. Cấp role mới mà họ vừa chọn
                role_id = role_mapping[emoji_name]
                new_role = guild.get_role(role_id)
                
                if new_role:
                    await member.add_roles(new_role)
                    print(f'🟢 Đã cấp {role_type} [{new_role.name}] cho [{member.name}]')
        else:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)
            
            try:
                await member.send("❌ Bạn cần là **Server Booster** để chọn các role đặc biệt này nhé!")
                print(f'🔴 Đã chặn [{member.name}] vì không phải Booster.')
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
                print(f'⚪ Đã thu hồi role [{role.name}] của [{member.name}] do bỏ thả tim.')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try:
        msg_mau = await ctx.channel.fetch_message(1507323471984722030)
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]:
            await msg_mau.add_reaction(emoji)
    except Exception as e:
        print(f"Lỗi setup bảng màu: {e}")

    try:
        msg_icon = await ctx.channel.fetch_message(1507323572824309780)
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]:
            await msg_icon.add_reaction(emoji)
    except Exception as e:
        print(f"Lỗi setup bảng icon: {e}")
    
    await ctx.send("✅ Đã setup xong các nút thả tim!", delete_after=5)

# === GỌI LỆNH CHẠY ===
keep_alive() # Khởi động Web Server ảo
bot.run(TOKEN) # Khởi động Bot