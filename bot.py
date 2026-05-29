import discord
from discord.ext import commands, tasks
from discord import app_commands
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
TOKEN = os.environ.get('DISCORD_TOKEN') 

SERVER_ID = 995320755002814514 # ID Server Tuglar
BOOSTER_ROLE_ID = 1000062456007249930 # ID role Server Booster gốc
LOG_CHANNEL_ID = 995612550383292458 # Kênh gửi thông báo level up

BOOSTER_TIERS = {
    7: 1509967931675640039,  # Booster I
    14: 1509970643993628672, # Booster II
    21: 1509970708850020523, # Booster III
    28: 1509970736767438879, # Booster IV
    35: 1509970770305224918, # Booster V
    42: 1509970819932094584, # Booster VI
    49: 1509970853192798259, # Booster VII
    56: 1509962710928982288  # Booster VIII
}

BOOSTER_EMOJIS = {
    1509967931675640039: "<:IR_Booster_I:1509974377481895966>",
    1509970643993628672: "<:IR_Booster_II:1509974379474194683>",
    1509970708850020523: "<:IR_Booster_III:1509974381584056552>",
    1509970736767438879: "<:IR_Booster_IV:1509974383396130980>",
    1509970770305224918: "<:IR_Booster_V:1509974385778495619>",
    1509970819932094584: "<:IR_Booster_VI:1509974388773228754>",
    1509970853192798259: "<:IR_Booster_VII:1509974390849147161>",
    1509962710928982288: "<:IR_Booster_VIII:1509974393227575506>"
}

MESSAGE_CONFIGS = {
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

# === GIAO DIỆN LỆNH /BOOSTER VỚI EMBED XỊN XÒ ===
class BoosterRoleSelect(discord.ui.Select):
    def __init__(self, placeholder, options, role_group_ids):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)
        self.role_group_ids = role_group_ids

    async def callback(self, interaction: discord.Interaction):
        selected_role_id = int(self.values[0])
        guild = interaction.guild
        member = interaction.user
        
        roles_to_remove = [guild.get_role(r) for r in self.role_group_ids if guild.get_role(r) and guild.get_role(r) in member.roles]
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
            
        if selected_role_id == 0:
            await interaction.response.send_message("🗑️ Đã thu hồi role thành công!", ephemeral=True)
            return
            
        new_role = guild.get_role(selected_role_id)
        if new_role:
            await member.add_roles(new_role)
            await interaction.response.send_message(f"✨ Bạn đã trang bị role: **{new_role.name}**", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Lỗi: Role không tồn tại trên hệ thống.", ephemeral=True)

class BoosterMenuView(discord.ui.View):
    def __init__(self, user_tier):
        super().__init__(timeout=300) 
        
        # ====== CHỈNH SỬA EMOJI Ở MENU MÀU ======
        if user_tier >= 1:
            color_options = [
                discord.SelectOption(label="Gỡ Role Màu", description="Hủy chọn màu hiện tại", value="0", emoji="❌"),
                discord.SelectOption(label="Sky", value="1162545019123666984", emoji="1️⃣"),
                discord.SelectOption(label="Peachy", value="1157298054764974130", emoji="2️⃣"),
                discord.SelectOption(label="Carrot", value="1157296480722366555", emoji="3️⃣"),
                discord.SelectOption(label="Rose", value="1157297666879926304", emoji="4️⃣"),
                discord.SelectOption(label="Purple", value="1157298499461840906", emoji="5️⃣")
            ]
            color_ids = [1162545019123666984, 1157298054764974130, 1157296480722366555, 1157297666879926304, 1157298499461840906]
            # Placeholder không hỗ trợ custom emoji nên dùng icon vẽ mặc định
            self.add_item(BoosterRoleSelect("🎨 Solid Color Pack", color_options, color_ids))
            
        # ====== CHỈNH SỬA EMOJI Ở MENU ICON ======
        if user_tier >= 2:
            icon_options = [
                discord.SelectOption(label="Gỡ Role Icon", description="Hủy chọn icon hiện tại", value="0", emoji="❌"),
                discord.SelectOption(label="Galactic Chrome", value="1164764867769667664", emoji="<:Staff_FA:1509995186644713646>"),
                discord.SelectOption(label="Holo", value="1164766440335876126", emoji="2️⃣"),
                discord.SelectOption(label="Sakura", value="1164946156858650635", emoji="3️⃣"),
                discord.SelectOption(label="Sherbet Dreamsicle", value="1164946570920337538", emoji="4️⃣")
            ]
            icon_ids = [1164764867769667664, 1164766440335876126, 1164946156858650635, 1164946570920337538]
            self.add_item(BoosterRoleSelect("✨ Chọn Role Icon (Đã mở khóa ở LV 2)", icon_options, icon_ids))

@bot.tree.command(name="booster", description="Mở giao diện chọn role độc quyền dành cho Server Booster")
async def booster_cmd(interaction: discord.Interaction):
    tier_levels = {
        1509967931675640039: 1, 
        1509970643993628672: 2, 
        1509970708850020523: 3, 
        1509970736767438879: 4, 
        1509970770305224918: 5, 
        1509970819932094584: 6, 
        1509970853192798259: 7, 
        1509962710928982288: 8  
    }
    
    member = interaction.user
    user_tier = 0
    current_emoji = "✨"
    
    for role in member.roles:
        if role.id in tier_levels:
            if tier_levels[role.id] > user_tier:
                user_tier = tier_levels[role.id]
                current_emoji = BOOSTER_EMOJIS.get(role.id, "✨")
                
    if user_tier == 0:
        await interaction.response.send_message("❌ Bạn cần đạt ít nhất cấp **Booster I** (Boost 1 tuần) để mở khóa giao diện này!", ephemeral=True)
        return
        
    days_boosted = 0
    if member.premium_since:
        now = discord.utils.utcnow()
        days_boosted = (now - member.premium_since).days
        
    milestones = sorted(BOOSTER_TIERS.keys()) 
    next_milestone = None
    for m in milestones:
        if days_boosted < m:
            next_milestone = m
            break
            
    if next_milestone:
        percent = min(100, int((days_boosted / next_milestone) * 100))
        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        progress_text = f"**Tiến độ lên cấp tiếp theo:** {days_boosted} / {next_milestone} ngày\n`[{bar}] {percent}%`"
    else:
        progress_text = "**Tiến độ nâng cấp:** Đã đạt cấp độ Tối Đa 🏆\n`[██████████] 100%`"

    embed = discord.Embed(
        title=f"Kho Đồ Độc Quyền | Booster LV {user_tier}",
        description=f"Cảm ơn bạn đã đồng hành cùng Server! Dưới đây là các phần thưởng bạn đã mở khóa.\n\n**Huy hiệu Booster:** {current_emoji}\n{progress_text}\n\n👇 **Sử dụng menu bên dưới để trang bị role:**",
        color=0xff73fa 
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    view = BoosterMenuView(user_tier)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
# ==============================================

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
                old_role_name = "Booster"
                
                target_role = guild.get_role(highest_role_id)
                if target_role and target_role not in member.roles:
                    roles_to_add.append(target_role)
                    
                    for r_id in all_tier_roles:
                        if r_id != highest_role_id:
                            old_role = guild.get_role(r_id)
                            if old_role and old_role in member.roles:
                                roles_to_remove.append(old_role)
                                old_role_name = old_role.name
                                
                    if roles_to_add:
                        await member.add_roles(*roles_to_add)
                        
                        log_channel = bot.get_channel(LOG_CHANNEL_ID)
                        if log_channel:
                            emoji = BOOSTER_EMOJIS.get(highest_role_id, "✨")
                            msg = f"> {emoji}・Chúc mừng {member.mention} đã nâng cấp role **{old_role_name}** lên **{target_role.name}**"
                            await log_channel.send(msg)
                            
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

# --- 3. CÁC TÍNH NĂNG PICK ROLE & ĐỒNG BỘ LỆNH ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã sẵn sàng phục vụ server!')
    
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Đã đồng bộ thành công {len(synced)} lệnh Slash (/)")
    except Exception as e:
        print(f"⚠️ Lỗi đồng bộ lệnh: {e}")

    if not check_booster_level.is_running():
        check_booster_level.start()
        print('⏳ Hệ thống auto Tiến Hóa Booster đã được kích hoạt!')
    print('-------------------------------------------')

# --- 4. GIỮ LẠI CƠ CHẾ THẢ TIM CŨ (Chạy song song) ---
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot: return
    if payload.message_id in MESSAGE_CONFIGS:
        guild = bot.get_guild(payload.guild_id)
        member = payload.member
        config = MESSAGE_CONFIGS[payload.message_id]
        role_mapping = config["mapping"]
        
        has_booster = any(role.id == BOOSTER_ROLE_ID for role in member.roles)

        if has_booster:
            emoji_name = payload.emoji.name
            if emoji_name in role_mapping:
                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)

                roles_to_remove = []
                for mapped_emoji, mapped_role_id in role_mapping.items():
                    if mapped_emoji != emoji_name: 
                        try: await message.remove_reaction(mapped_emoji, member)
                        except Exception: pass
                            
                        old_role = guild.get_role(mapped_role_id)
                        if old_role and old_role in member.roles:
                            roles_to_remove.append(old_role)
                
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)

                role_id = role_mapping[emoji_name]
                new_role = guild.get_role(role_id)
                if new_role: await member.add_roles(new_role)
        else:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)
            try: await member.send("❌ Bạn cần là **Server Booster** để chọn các role đặc biệt này nhé!")
            except discord.Forbidden: pass

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in MESSAGE_CONFIGS:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member is None or member.bot: return

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
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]: await msg_mau.add_reaction(emoji)
    except Exception: pass
    try:
        msg_icon = await ctx.channel.fetch_message(1507323572824309780)
        for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]: await msg_icon.add_reaction(emoji)
    except Exception: pass
    await ctx.send("✅ Đã setup xong các nút thả tim!", delete_after=5)

# === GỌI LỆNH CHẠY ===
keep_alive() 
bot.run(TOKEN)