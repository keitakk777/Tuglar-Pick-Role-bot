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

# --- DANH SÁCH QUẢN LÝ LỘT ROLE TỰ ĐỘNG ---
ALL_COLOR_ROLES = [
    1162545019123666984, 1157298054764974130, 1157296480722366555, 1157297666879926304, 1157298499461840906, # Tier 0
    1164764867769667664, 1164766440335876126, 1510012176876699768, 1164946570920337538, 1164946156858650635  # Tier 1
]
ALL_ICON_ROLES = [] 

# ROLE FREE DÀNH CHO TẤT CẢ MỌI NGƯỜI (Điền ID role Ping, Game, Giới tính... vào đây)
FREE_PING_ROLES = [111111111111111111, 222222222222222222] 
# ------------------------------------------

BOOSTER_TIERS = {
    7: 1509967931675640039,
    14: 1509970643993628672,
    21: 1509970708850020523,
    28: 1509970736767438879,
    35: 1509970770305224918,
    42: 1509970819932094584,
    49: 1509970853192798259,
    56: 1509962710928982288
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
            "1️⃣": 1162545019123666984, "2️⃣": 1157298054764974130, "3️⃣": 1157296480722366555,
            "4️⃣": 1157297666879926304, "5️⃣": 1157298499461840906 
        }
    },
    1507323572824309780: { 
        "type": "Icon",
        "mapping": {
            "1️⃣": 1164764867769667664, "2️⃣": 1164766440335876126, "3️⃣": 1164946156858650635,
            "4️⃣": 1164946570920337538 
        }
    }
}
# ============================================

# === GIAO DIỆN LỆNH /PROFILE MỚI ===
class GenericRoleSelect(discord.ui.Select):
    def __init__(self, placeholder, options, role_group_ids, max_val=1):
        super().__init__(placeholder=placeholder, min_values=1, max_values=max_val, options=options)
        self.role_group_ids = role_group_ids

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        
        # Nếu là Menu gỡ role tự động (chỉ chọn 1)
        if self.max_values == 1:
            selected_role_id = int(self.values[0])
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
                await interaction.response.send_message("❌ Lỗi: Role không tồn tại.", ephemeral=True)

class ClearBoosterRolesButton(discord.ui.Button):
    def __init__(self, all_pickable_role_ids):
        super().__init__(style=discord.ButtonStyle.danger, label="Gỡ Toàn Bộ Màu & Icon", emoji="🗑️", row=3)
        self.all_pickable_role_ids = all_pickable_role_ids

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        roles_to_remove = [guild.get_role(r) for r in self.all_pickable_role_ids if guild.get_role(r) and guild.get_role(r) in member.roles]
        
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove)
            await interaction.response.send_message("🗑️ Đã gỡ toàn bộ Role Màu & Icon thành công!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Bạn hiện không trang bị Role Màu hay Icon nào để gỡ.", ephemeral=True)

class ProfileMenuView(discord.ui.View):
    def __init__(self, user_tier):
        super().__init__(timeout=300) 
        
        # ====== 1. MENU ROLE FREE (AI CŨNG THẤY) ======
        # (Bạn sửa ID và Tên ở đây cho phù hợp với server nhé)
        free_options = [
            discord.SelectOption(label="Hủy nhận Thông báo", description="Không nhận ping nữa", value="0", emoji="🔕"),
            discord.SelectOption(label="Ping Sự Kiện", description="Nhận thông báo event mới", value="111111111111111111", emoji="🎉"),
            discord.SelectOption(label="Ping Mini-game", description="Tham gia chơi game cùng server", value="222222222222222222", emoji="🎮")
        ]
        self.add_item(GenericRoleSelect("📌 Chọn Role Thông Báo (Miễn phí)", free_options, FREE_PING_ROLES, max_val=1))
        
        # ====== 2. MENU MÀU BOOSTER ======
        all_booster_ids = []
        if user_tier >= 1:
            color_options = [
                discord.SelectOption(label="Gỡ Role Màu", value="0", emoji="❌"),
                discord.SelectOption(label="Sky", value="1162545019123666984", emoji="<:IC_Sky:1509998906723799191>"),
                discord.SelectOption(label="Carrot", value="1157296480722366555", emoji="<:IC_Carrot:1510003170661892399>"),
                discord.SelectOption(label="Rose", value="1157297666879926304", emoji="<:IC_Rose:1510003959652155556>"),
                discord.SelectOption(label="Purple", value="1157298499461840906", emoji="<:IC_Purple:1510004463362900229>"),
                discord.SelectOption(label="Peachy", value="1157298054764974130", emoji="<:IC_Peachy:1509997745916612768>")
            ]
            color_ids = [1162545019123666984, 1157298054764974130, 1157296480722366555, 1157297666879926304, 1157298499461840906]
            all_booster_ids.extend(ALL_COLOR_ROLES)
            self.add_item(GenericRoleSelect("🎨 Color Pack - Booster Gốc", color_options, ALL_COLOR_ROLES))
            
        # ====== 3. MENU ICON BOOSTER ======
        if user_tier >= 2:
            icon_options = [
                discord.SelectOption(label="Gỡ Role Màu", value="0", emoji="❌"),
                discord.SelectOption(label="Mint", value="1164764867769667664", emoji="<:IC_Mint:1510016060982558731>"),
                discord.SelectOption(label="xLemon", value="1164766440335876126", emoji="<:IC_xLemon:1510016065122336929>"),
                discord.SelectOption(label="1stHeart", value="1510012176876699768", emoji="<:IC_1stHeart:1510016047896334536>"),
                discord.SelectOption(label="Cyber-20xx", value="1164946570920337538", emoji="<:IC_Cyber20xx:1510016058613043230>"),
                discord.SelectOption(label="TraDaoCamSa", value="1164946156858650635", emoji="<:IC_TraDaoCamSa:1510016063125852410>")
            ]
            all_booster_ids.extend(ALL_ICON_ROLES)
            self.add_item(GenericRoleSelect("🎨 Color Pack - Booster I", icon_options, ALL_COLOR_ROLES)) # Tạm thời dùng Color Roles theo setup của bạn
            
        # Nút Gỡ Booster (Chỉ hiện nếu có mở khóa Booster Menu)
        if all_booster_ids:
            self.add_item(ClearBoosterRolesButton(list(set(all_booster_ids))))

@bot.tree.command(name="profile", description="Mở hồ sơ cá nhân để nhận Role Free và Quản lý Đồ Booster")
async def profile_cmd(interaction: discord.Interaction):
    tier_levels = {
        BOOSTER_ROLE_ID: 1,      
        1509967931675640039: 2,  
        1509970643993628672: 3,  
        1509970708850020523: 4,  
        1509970736767438879: 5,  
        1509970770305224918: 6,  
        1509970819932094584: 7,  
        1509970853192798259: 8,  
        1509962710928982288: 9   
    }
    
    tier_names = {
        1: "Booster Gốc", 2: "Booster I", 3: "Booster II", 4: "Booster III",
        5: "Booster IV", 6: "Booster V", 7: "Booster VI", 8: "Booster VII", 9: "Booster VIII"
    }
    
    member = interaction.user
    user_tier = 0
    current_emoji = "💖" 
    
    for role in member.roles:
        if role.id in tier_levels:
            if tier_levels[role.id] > user_tier:
                user_tier = tier_levels[role.id]
                current_emoji = BOOSTER_EMOJIS.get(role.id, "💖")
                
    # --- GIAO DIỆN DÀNH CHO MEMBER THƯỜNG ---
    if user_tier == 0:
        embed = discord.Embed(
            title="👤 Hồ Sơ Của Bạn | Thành Viên Thường",
            description="Chào mừng bạn đến với mục quản lý hồ sơ!\n\n👇 **Bạn có thể nhận các Role Cơ Bản ở menu bên dưới.**\n\n✨ **Đặc quyền Độc Quyền:** Nâng cấp lên Server Booster ngay hôm nay để mở khóa **Kho Đồ Độc Quyền** gồm các gói Màu Tên và Icon lấp lánh cạnh tên bạn nhé!",
            color=0x3498db # Màu xanh member thường
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        view = ProfileMenuView(user_tier)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        return
        
    # --- GIAO DIỆN DÀNH CHO BOOSTER ---
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

    tier_title = tier_names.get(user_tier, "Booster")

    embed = discord.Embed(
        title=f"💎 Hồ Sơ Độc Quyền | {tier_title}",
        description=f"Cảm ơn bạn đã đồng hành cùng Server! Dưới đây là các phần thưởng bạn đã mở khóa.\n\n**Huy hiệu Booster:** {current_emoji}\n{progress_text}\n\n👇 **Quản lý Role Free và Đồ Booster ở menu bên dưới:**",
        color=0xff73fa # Màu hồng Nitro
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    
    view = ProfileMenuView(user_tier)
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
        roles_to_remove = [after.guild.get_role(r_id) for r_id in all_tier_roles if after.guild.get_role(r_id) in after.roles]
        if roles_to_remove:
            await after.remove_roles(*roles_to_remove)

# --- 3. CÁC TÍNH NĂNG PICK ROLE THẢ TIM CŨ & ĐỒNG BỘ LỆNH ---
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã sẵn sàng phục vụ server!')
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Đã đồng bộ lệnh Slash (/). (Có lệnh /profile mới)")
    except Exception as e: print(f"⚠️ Lỗi đồng bộ: {e}")
    if not check_booster_level.is_running(): check_booster_level.start()

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot: return
    if payload.message_id in MESSAGE_CONFIGS:
        guild = bot.get_guild(payload.guild_id)
        member = payload.member
        config = MESSAGE_CONFIGS[payload.message_id]
        
        if any(role.id == BOOSTER_ROLE_ID for role in member.roles):
            emoji_name = payload.emoji.name
            if emoji_name in config["mapping"]:
                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                try: await message.remove_reaction(payload.emoji, member)
                except Exception: pass
                
                roles_to_check = ALL_COLOR_ROLES if config["type"] == "Màu" else ALL_ICON_ROLES
                roles_to_remove = [guild.get_role(r) for r in roles_to_check if guild.get_role(r) and guild.get_role(r) in member.roles]
                if roles_to_remove: await member.remove_roles(*roles_to_remove)

                new_role = guild.get_role(config["mapping"][emoji_name])
                if new_role: await member.add_roles(new_role)
        else:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)
            try: await member.send("❌ Bạn cần là **Server Booster** để chọn role này!")
            except discord.Forbidden: pass

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id in MESSAGE_CONFIGS:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member and not member.bot:
            emoji_name = payload.emoji.name
            if emoji_name in MESSAGE_CONFIGS[payload.message_id]["mapping"]:
                role = guild.get_role(MESSAGE_CONFIGS[payload.message_id]["mapping"][emoji_name])
                if role and role in member.roles: await member.remove_roles(role)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try:
        msg_mau = await ctx.channel.fetch_message(1507323471984722030)
        for e in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]: await msg_mau.add_reaction(e)
    except: pass
    try:
        msg_icon = await ctx.channel.fetch_message(1507323572824309780)
        for e in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]: await msg_icon.add_reaction(e)
    except: pass
    await ctx.send("✅ Đã setup xong nút thả tim!", delete_after=5)

# === GỌI LỆNH CHẠY ===
keep_alive() 
bot.run(TOKEN)