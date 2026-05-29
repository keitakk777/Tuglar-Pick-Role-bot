import discord
from discord.ext import commands, tasks
from discord import app_commands
from config import *

class GenericRoleSelect(discord.ui.Select):
    def __init__(self, placeholder, options, role_group_ids):
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)
        self.role_group_ids = role_group_ids
        
    def get_selected_emoji(self, value_id):
        for option in self.options:
            if option.value == value_id:
                if option.emoji and option.emoji.id:
                    return f"<:{option.emoji.name}:{option.emoji.id}>"
                return option.emoji.name if option.emoji else "✨"
        return "✨"

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        
        selected_role_id = int(self.values[0])
        selected_emoji_str = self.get_selected_emoji(self.values[0])
        
        if selected_role_id == 0:
            roles_to_remove = [guild.get_role(r) for r in self.role_group_ids if guild.get_role(r) and guild.get_role(r) in member.roles]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            embed = discord.Embed(description="🗑️・Đã thu hồi role thành công!", color=0xff4757, timestamp=discord.utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        new_role = guild.get_role(selected_role_id)
        if not new_role:
            embed = discord.Embed(description="❌・Lỗi: Role không tồn tại.", color=0xff4757, timestamp=discord.utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if new_role in member.roles:
            await member.remove_roles(new_role)
            embed = discord.Embed(title=f"{selected_emoji_str} Bạn đã gỡ bỏ role: {new_role.name}", color=0xff4757, timestamp=discord.utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            roles_to_remove = [guild.get_role(r) for r in self.role_group_ids if guild.get_role(r) and guild.get_role(r) in member.roles]
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
                
            await member.add_roles(new_role)
            embed = discord.Embed(title=f"{selected_emoji_str} Bạn đã trang bị role: {new_role.name}", color=0x2ecc71, timestamp=discord.utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
            embed = discord.Embed(description="🗑️・Đã gỡ toàn bộ Role Màu & Icon thành công!", color=0xff4757, timestamp=discord.utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description="⚠️・Bạn hiện không trang bị Role Màu hay Icon nào để gỡ.", color=0xf1c40f, timestamp=discord.utils.utcnow())
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ProfileMenuView(discord.ui.View):
    def __init__(self, user_tier):
        super().__init__(timeout=300) 
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
            all_booster_ids.extend(ALL_COLOR_ROLES)
            self.add_item(GenericRoleSelect("🎨 Color Pack - Booster Gốc", color_options, ALL_COLOR_ROLES))
            
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
            self.add_item(GenericRoleSelect("🎨 Color Pack - Booster I", icon_options, ALL_COLOR_ROLES)) 
            
        if all_booster_ids:
            self.add_item(ClearBoosterRolesButton(list(set(all_booster_ids))))


class BoosterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_booster_level.is_running():
            self.check_booster_level.start()
            print('⏳ Cogs: Hệ thống auto Tiến Hóa Booster đã kích hoạt!')

    @tasks.loop(hours=24)
    async def check_booster_level(self):
        guild = self.bot.get_guild(SERVER_ID)
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
                            log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
                            if log_channel:
                                emoji = BOOSTER_EMOJIS.get(highest_role_id, "✨")
                                embed = discord.Embed(
                                    description=f"> {emoji}・Chúc mừng {member.mention} đã nâng cấp role **{old_role_name}** lên **{target_role.name}**",
                                    color=0xff73fa, timestamp=discord.utils.utcnow()
                                )
                                embed.set_footer(text=FOOTER_TEXT)
                                await log_channel.send(embed=embed)
                                
                        if roles_to_remove:
                            await member.remove_roles(*roles_to_remove)
            else:
                roles_to_remove = [guild.get_role(r_id) for r_id in all_tier_roles if guild.get_role(r_id) and guild.get_role(r_id) in member.roles]
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove)

    @check_booster_level.before_loop
    async def before_check_booster_level(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is not None and after.premium_since is None:
            all_tier_roles = list(BOOSTER_TIERS.values())
            roles_to_remove = [after.guild.get_role(r_id) for r_id in all_tier_roles if after.guild.get_role(r_id) in after.roles]
            if roles_to_remove:
                await after.remove_roles(*roles_to_remove)

    @app_commands.command(name="profile", description="Xem hồ sơ và tùy chỉnh role độc quyền")
    async def profile_cmd(self, interaction: discord.Interaction):
        tier_levels = { BOOSTER_ROLE_ID: 1, 1509967931675640039: 2, 1509970643993628672: 3, 1509970708850020523: 4, 1509970736767438879: 5, 1509970770305224918: 6, 1509970819932094584: 7, 1509970853192798259: 8, 1509962710928982288: 9 }
        tier_names = { 1: "Booster Gốc", 2: "Booster I", 3: "Booster II", 4: "Booster III", 5: "Booster IV", 6: "Booster V", 7: "Booster VI", 8: "Booster VII", 9: "Booster VIII" }
        
        member = interaction.user
        user_tier = 0
        current_emoji = "💖" 
        for role in member.roles:
            if role.id in tier_levels:
                if tier_levels[role.id] > user_tier:
                    user_tier = tier_levels[role.id]
                    current_emoji = BOOSTER_EMOJIS.get(role.id, "💖")
                    
        if user_tier == 0:
            embed = discord.Embed(title="👤 Hồ Sơ Của Bạn | Thành Viên Thường", description="Chào mừng bạn đến với mục quản lý hồ sơ!\n\n👇 **Để nhận thông báo (Ping Server, Event...), hãy vào mục <id:customize>.**\n\n✨ **Đặc quyền Độc Quyền:** Boost Server để mở khóa các pack role độc đáo cạnh tên bạn nhé!", color=0x3498db, timestamp=discord.utils.utcnow())
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=FOOTER_TEXT)
            view = ProfileMenuView(user_tier)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return
            
        days_boosted = 0
        if member.premium_since:
            days_boosted = (discord.utils.utcnow() - member.premium_since).days
            
        milestones = sorted(BOOSTER_TIERS.keys()) 
        next_milestone = next((m for m in milestones if days_boosted < m), None)
                
        if next_milestone:
            percent = min(100, int((days_boosted / next_milestone) * 100))
            filled = int(percent / 10)
            bar = "█" * filled + "░" * (10 - filled)
            progress_text = f"**Tiến độ lên cấp tiếp theo:** {days_boosted} / {next_milestone} ngày\n`[{bar}] {percent}%`"
        else:
            progress_text = "**Tiến độ nâng cấp:** Đã đạt cấp độ Tối Đa 🏆\n`[██████████] 100%`"

        tier_title = tier_names.get(user_tier, "Booster")
        embed = discord.Embed(title=f"💎 Hồ Sơ Độc Quyền | {tier_title}", description=f"Cảm ơn bạn đã đồng hành cùng Server! Dưới đây là các phần thưởng bạn đã mở khóa.\n\n**Huy hiệu Booster:** {current_emoji}\n{progress_text}\n\n👇 **Quản lý Role Booster ở menu bên dưới:**\n*(Để nhận Ping thông báo, vui lòng vào <id:customize>)*", color=0xff73fa, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=FOOTER_TEXT)
        view = ProfileMenuView(user_tier)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="index", description="Sổ tay Role Đảo Tuglar (Hoặc tra cứu role bất kỳ)")
    @app_commands.describe(role="Chọn role bạn muốn tra cứu (Bỏ trống để mở trang Sổ Tay tổng hợp)")
    async def index_cmd(self, interaction: discord.Interaction, role: discord.Role = None):
        guild = interaction.guild
        
        if role:
            cach_nhan = "Đang cập nhật... (Role ẩn hoặc Role Sự kiện)"
            dac_quyen = "Chưa có thông tin"
            
            if role.id == BOOSTER_ROLE_ID:
                cach_nhan = "Nạp Boost cho Server (Mở khóa Tier 0)"
                dac_quyen = "<:perk_collection:1193667977405534218> Truy cập Kho đồ Màu Sắc"
            elif role.id in ALL_COLOR_ROLES or role.id in ALL_ICON_ROLES:
                cach_nhan = "Mở khóa từ Đặc quyền Booster (Dùng lệnh `/profile`)"
                dac_quyen = "<:perk_displayseperately:1193783034323931207> Trang trí Profile"
            elif role.permissions.administrator:
                cach_nhan = "Role đặc quyền dành cho Ban Quản Trị"
                dac_quyen = "Toàn quyền quản lý Server"

            so_nguoi = len(role.members) 
            
            content = (
                f"## {role.mention}\n"
                f"> - Cách nhận: **{cach_nhan}**\n"
                f"> - Đặc quyền: {dac_quyen}\n"
                f"> - Sở hữu: `{so_nguoi}`\n"
            )
            await interaction.response.send_message(content, ephemeral=False)
            return

        def count_role(role_id):
            r = guild.get_role(role_id)
            return len(r.members) if r else 0

        content = f"""# <:TugIsl_search:1169899042411655229> SỔ TAY ROLE ĐẢO TUGLAR #
## <:TugIsl_icon_filter:1169910021644111932> Phân loại role ##
> - Các role trong server được chia ra làm nhiều loại khác nhau. Mỗi loại có cách sở hữu và đặc quyền ưu tiên khác nhau.
> - Hiện tại, server có các phân loại chính: 

### <:TugIsl_icon_bag:1189471543886090313> Collection Role ###
> - Các role custom, role tùy biến (đặc quyền từ role khác) sẽ ở phân loại này.
> - Các role này có thể được hiển thị hoặc ẩn ở danh mục ✨ Bộ Sưu Tập

### <:TugIsl_icon_star:1189471573401419827> Special Role ###
> Các role này thường chỉ dành cho một số người với các tiêu chí để nhận, đặc biệt hơn so với achievement role 

### <:TugIsl_icon_event:1182752944156844093> Event Role  ###
> - Các role này thường chỉ xuất hiện **1 lần duy nhất** với các sự kiện để đánh dấu lại cột mốc thời gian bạn đã đồng hành cùng với server.

### <:TugIsl_icon_compass:1189060875299078275> Achievement Role  ###
> Các role này nhận được khi hoàn thành yêu cầu nhất định trong server. Thường không giới hạn thời gian nên dễ sở hữu.

# <:TugIsl_icon_event:1182752944156844093> Event Role
## <@&1157198996234842143> <:1anni:1510063186429083648>
> - Ra mắt: <t:1688835600:R>
> - Cách nhận: **Tham gia SK SN 1 Tuổi Đảo Tuglar**
> - Sở hữu: `{count_role(1157198996234842143)}`
## <@&1169623255297032272> <:winterlands2023:1510063146583199994>
> - Ra mắt: <t:1698771600:R>
> - Cách nhận: **Tưới cây thông noel 🎄**
> - Sở hữu: `{count_role(1169623255297032272)}`
## <@&1189375452603756645> <:tet2024:1510063134415650946> 
> - Ra mắt: <t:1706720400:R>
> - Cách nhận: **Đổi mảnh 🧩 - Sự kiện Trang trí Tết 2024**
> - Sở hữu: `{count_role(1189375452603756645)}`"""
        
        await interaction.response.send_message(content, ephemeral=False)

async def setup(bot):
    await bot.add_cog(BoosterCog(bot))