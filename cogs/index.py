import discord
from discord.ext import commands
from discord import app_commands
from config import *

# Từ điển chứa thông tin cụ thể của các Role Sự Kiện và Special Role
ROLE_INFO_DB = {
    # --- EVENT ROLES ---
    1466299698800365695: {"cach_nhan": "Chat trong server trong thời gian diễn ra Sự kiện Tết Bính Ngọ 2026", "dac_quyen": "Huy hiệu kỷ niệm Sự kiện Tết 2026"},
    1274907870701424755: {"cach_nhan": "Thu thập nguyên liệu làm Bánh Trung Thu 🥮 tại Sự kiện Tết Trung Thu 2024", "dac_quyen": "Huy hiệu kỷ niệm Trung Thu 2024"},
    1240597343049486397: {"cach_nhan": "Gửi lời chúc mừng sinh nhật server tròn 2 tuổi", "dac_quyen": "Huy hiệu kỷ niệm 2 Năm Thành Lập"},
    1189375452603756645: {"cach_nhan": "Đổi mảnh 🧩 tại Sự kiện Trang trí Tết Giáp Thìn 2024", "dac_quyen": "Huy hiệu kỷ niệm Tết Giáp Thìn 2024"},
    1157198996234842143: {"cach_nhan": "Tham gia Sự kiện Sinh Nhật 1 Tuổi Đảo Tuglar", "dac_quyen": "Huy hiệu kỷ niệm 1 Năm Thành Lập"},
    1169623255297032272: {"cach_nhan": "Tưới cây thông noel 🎄 trong thời gian diễn ra Sự kiện Winterlands 2023", "dac_quyen": "Huy hiệu kỷ niệm Winterlands 2023"},
    
    # --- SPECIAL ROLES ---
    1346173590642622528: {"cach_nhan": "Tham gia Quân đoàn Free Fire Đảo Tuglar", "dac_quyen": "Thành viên Quân đoàn chính thức"},
    1175019718466359306: {"cach_nhan": "Tham gia Clan Liên Quân TuglarPars", "dac_quyen": "Thành viên Clan Liên Quân"},
    1113018418300452894: {"cach_nhan": "Tham gia CLB Par.", "dac_quyen": "Thành viên Câu lạc bộ Par."},
}

# === CÁC LỚP GIAO DIỆN (UI VIEWS) CHO INDEX ===
class IndexPaginationView(discord.ui.View):
    def __init__(self, pages, bot_avatar_url):
        super().__init__(timeout=180) 
        self.pages = pages
        self.current_page = 0
        self.bot_avatar_url = bot_avatar_url
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1
        self.page_indicator.label = f"Trang {self.current_page + 1}/{len(self.pages)}"

    def get_current_embed(self):
        embed = discord.Embed(
            description=self.pages[self.current_page],
            color=0xff73fa,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=self.bot_avatar_url)
        embed.set_footer(text=FOOTER_TEXT)
        return embed

    @discord.ui.button(label="◀ Trước", style=discord.ButtonStyle.primary, custom_id="prev_page")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_embed(), view=self)

    @discord.ui.button(label="Trang X/Y", style=discord.ButtonStyle.secondary, disabled=True, custom_id="page_indicator")
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass 

    @discord.ui.button(label="Sau ▶", style=discord.ButtonStyle.primary, custom_id="next_page")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_embed(), view=self)


# === MODULE COG CHO INDEX ===
class IndexCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="index", description="Sổ tay Role Đảo Tuglar (Hoặc tra cứu role bất kỳ)")
    @app_commands.describe(role="Chọn role bạn muốn tra cứu (Bỏ trống để mở trang Sổ Tay tổng hợp)")
    async def index_cmd(self, interaction: discord.Interaction, role: discord.Role = None):
        guild = interaction.guild
        bot_avatar_url = self.bot.user.display_avatar.url
        
        # ====== KỊCH BẢN 1: TRA CỨU ROLE BẤT KỲ ======
        if role:
            cach_nhan = "Đang cập nhật... (Role ẩn hoặc Role Sự kiện)"
            dac_quyen = "Chưa có thông tin"
            
            # 1. Kiểm tra xem role có trong Từ điển Sự Kiện/Đặc biệt không
            if role.id in ROLE_INFO_DB:
                cach_nhan = ROLE_INFO_DB[role.id]["cach_nhan"]
                dac_quyen = ROLE_INFO_DB[role.id]["dac_quyen"]
            # 2. Kiểm tra các Role Hệ thống (Booster, Màu)
            elif role.id == BOOSTER_ROLE_ID:
                cach_nhan = "Nạp Boost cho Server (Mở khóa Tier 0)"
                dac_quyen = "<:perk_collection:1193667977405534218> Truy cập Kho đồ Màu Sắc"
            elif role.id in ALL_COLOR_ROLES or role.id in ALL_ICON_ROLES:
                cach_nhan = "Mở khóa từ Đặc quyền Booster (Dùng lệnh `/profile`)"
                dac_quyen = "<:perk_displayseperately:1193783034323931207> Trang trí Profile"
            elif role.permissions.administrator:
                cach_nhan = "Role đặc quyền dành cho Ban Quản Trị"
                dac_quyen = "Toàn quyền quản lý Server"

            so_nguoi = len(role.members) 
            
            embed_role = discord.Embed(
                title="🔍 KẾT QUẢ TRA CỨU ROLE",
                description=(
                    f"## {role.mention}\n"
                    f" - Cách nhận: **{cach_nhan}**\n"
                    f" - Đặc quyền: {dac_quyen}\n"
                    f" - Sở hữu: `{so_nguoi}` người\n"
                ),
                color=role.color if role.color.value != 0 else 0xff73fa,
                timestamp=discord.utils.utcnow()
            )
            embed_role.set_thumbnail(url=bot_avatar_url)
            embed_role.set_footer(text=FOOTER_TEXT)

            await interaction.response.send_message(embed=embed_role, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())
            return

        # ====== KỊCH BẢN 2: MỞ SỔ TAY TỔNG HỢP (PHÂN TRANG) ======
        def count_role(role_id):
            r = guild.get_role(role_id)
            return len(r.members) if r else 0

        page_1 = """# 📘 SỔ TAY ROLE ĐẢO TUGLAR #
### ⚜️ Special Role ###
 Các role này thường chỉ dành cho một số người với các tiêu chí để nhận, đặc biệt hơn so với achievement role.

### 🎉 Event Role  ###
 - Các role này thường chỉ xuất hiện **1 lần duy nhất** với các sự kiện để đánh dấu lại cột mốc thời gian bạn đã đồng hành cùng với server."""

        page_2 = f"""# 🎉 Event Role (Trang 1)
## <@&1466299698800365695> <:tet2026:1510063136831705270>
 - Ra mắt: <t:1771200240:D>
 - Cách nhận: **Chat trong server trong thời gian diễn ra Sự kiện Tết Bính Ngọ 2026**
 - Sở hữu: `{count_role(1466299698800365695)}`
## <@&1274907870701424755> <:trungthu2024:1510063138970800219>
 - Ra mắt: <t:1724112240:D>
 - Cách nhận: **Thu thập nguyên liệu làm Bánh Trung Thu 🥮 tại Sự kiện Tết Trung Thu 2024**
 - Sở hữu: `{count_role(1274907870701424755)}`
## <@&1240597343049486397> <:2anni:1510063188543275118>
 - Ra mắt: <t:1720483440:D>
 - Cách nhận: **Gửi lời chúc mừng sinh nhật server tròn 2 tuổi**
 - Sở hữu: `{count_role(1240597343049486397)}`"""

        page_3 = f"""# 🎉 Event Role (Trang 2)
## <@&1189375452603756645> <:tet2024:1510063134415650946> 
 - Ra mắt: <t:1706720400:D>
 - Cách nhận: **Đổi mảnh 🧩 tại Sự kiện Trang trí Tết Giáp Thìn 2024**
 - Sở hữu: `{count_role(1189375452603756645)}`
## <@&1157198996234842143> <:1anni:1510063186429083648>
 - Ra mắt: <t:1688861040:D>
 - Cách nhận: **Tham gia SK SN 1 Tuổi Đảo Tuglar**
 - Sở hữu: `{count_role(1157198996234842143)}`
## <@&1169623255297032272> <:winterlands2023:1510063146583199994>
 - Ra mắt: <t:1698771600:D>
 - Cách nhận: **Tưới cây thông noel 🎄 trong thời gian diễn ra Sự kiện Winterlands 2023**
 - Sở hữu: `{count_role(1169623255297032272)}`"""

        page_4 = f"""# ⚜️ Special Role
## <@&1346173590642622528> <:DaoTuglarClanOld:1510063131584626688>
 - Ra mắt: <t:1688835600:D>
 - Cách nhận: **Tham gia Quân đoàn Free Fire Đảo Tuglar**
 - Sở hữu: `{count_role(1346173590642622528)}`
## <@&1175019718466359306> <:TuglarPars:1510063144532316242>
 - Ra mắt: Chưa cập nhật
 - Cách nhận: **Tham gia Clan Liên Quân TuglarPars**
 - Sở hữu: `{count_role(1175019718466359306)}`
## <@&1113018418300452894> <:TuglarPars:1510063144532316242>
 - Ra mắt: Chưa cập nhật
 - Cách nhận: **Tham gia CLB Par.**
 - Sở hữu: `{count_role(1113018418300452894)}`"""

        pages = [page_1, page_2, page_3, page_4]
        
        view = IndexPaginationView(pages, bot_avatar_url)
        embed_index = view.get_current_embed()

        await interaction.response.send_message(embed=embed_index, view=view, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())

async def setup(bot):
    await bot.add_cog(IndexCog(bot))