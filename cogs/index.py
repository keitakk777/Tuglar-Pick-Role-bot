import discord
from discord.ext import commands
from discord import app_commands
from config import *

# === ĐỊNH NGHĨA EMOJI ===
EMOJI_EVENT = "<:TI_ultev:1524079014845743235>"
EMOJI_SPECIAL = "<:TI_ultspecial:1524079822072971444>"

# === KHO DỮ LIỆU TẬP TRUNG CHO ROLE ===
ROLE_INFO_DB = {
    # --- EVENT ROLES ---
    1466299698800365695: {"type": "event", "timestamp": "1771200240", "cach_nhan": "Tương tác trong server dịp Sự kiện Tết Bính Ngọ 2026", "dac_quyen": "Huy hiệu kỷ niệm Tết 2026"},
    1274907870701424755: {"type": "event", "timestamp": "1724112240", "cach_nhan": "Thu thập nguyên liệu Bánh Trung Thu tại Sự kiện 2024", "dac_quyen": "Huy hiệu kỷ niệm Trung Thu 2024"},
    1240597343049486397: {"type": "event", "timestamp": "1720483440", "cach_nhan": "Gửi lời chúc mừng Sinh nhật Server tròn 2 tuổi", "dac_quyen": "Huy hiệu kỷ niệm 2 Năm Thành Lập"},
    1189375452603756645: {"type": "event", "timestamp": "1706720400", "cach_nhan": "Đổi mảnh ghép tại Sự kiện Trang trí Tết Giáp Thìn 2024", "dac_quyen": "Huy hiệu kỷ niệm Tết Giáp Thìn 2024"},
    1157198996234842143: {"type": "event", "timestamp": "1688861040", "cach_nhan": "Tham gia chuỗi Sự kiện Sinh Nhật 1 Tuổi", "dac_quyen": "Huy hiệu kỷ niệm 1 Năm Thành Lập"},
    1169623255297032272: {"type": "event", "timestamp": "1698771600", "cach_nhan": "Tưới Cây thông Noel tại Sự kiện Winterlands 2023", "dac_quyen": "Huy hiệu kỷ niệm Winterlands 2023"},
    
    # --- SPECIAL ROLES ---
    1346173590642622528: {"type": "special", "timestamp": "1688835600", "cach_nhan": "Trở thành thành viên Quân đoàn Free Fire Đảo Tuglar", "dac_quyen": "Thành viên Quân đoàn chính thức"},
    1175019718466359306: {"type": "special", "timestamp": None, "cach_nhan": "Trở thành thành viên Clan Liên Quân TuglarPars", "dac_quyen": "Thành viên Clan Liên Quân"},
    1113018418300452894: {"type": "special", "timestamp": None, "cach_nhan": "Trở thành thành viên Câu lạc bộ Par.", "dac_quyen": "Thành viên Câu lạc bộ Par."},
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
        
        def count_role(role_id):
            r = guild.get_role(role_id)
            return len(r.members) if r else 0

        # ====== KỊCH BẢN 1: TRA CỨU ROLE BẤT KỲ ======
        if role:
            cach_nhan = "Đang cập nhật... (Role ẩn hoặc Role Sự kiện)"
            dac_quyen = "Chưa có thông tin"
            emoji_prefix = "🏷️"
            
            # 1. Kiểm tra xem role có trong Từ điển Sự Kiện/Đặc biệt không
            if role.id in ROLE_INFO_DB:
                info = ROLE_INFO_DB[role.id]
                cach_nhan = info["cach_nhan"]
                dac_quyen = info["dac_quyen"]
                emoji_prefix = EMOJI_EVENT if info["type"] == "event" else EMOJI_SPECIAL
                
            # 2. Kiểm tra các Role Hệ thống (Booster, Màu)
            elif role.id == BOOSTER_ROLE_ID:
                cach_nhan = "Nạp Boost cho Server (Mở khóa Tier 0)"
                dac_quyen = "Truy cập Kho đồ Màu Sắc"
                emoji_prefix = "💎"
            elif role.id in ALL_COLOR_ROLES or role.id in ALL_ICON_ROLES:
                cach_nhan = "Mở khóa từ Đặc quyền Booster (Dùng lệnh `/profile`)"
                dac_quyen = "Trang trí Profile cá nhân"
                emoji_prefix = "🎨"
            elif role.permissions.administrator:
                cach_nhan = "Role đặc quyền dành cho Ban Quản Trị"
                dac_quyen = "Toàn quyền quản lý Server"
                emoji_prefix = "👑"

            so_nguoi = count_role(role.id)
            
            embed_role = discord.Embed(
                title="🔍 KẾT QUẢ TRA CỨU ROLE",
                description=(
                    f"## {role.mention}\n"
                    f" - <:TI_ultinfo:1524096769414139996> Cách nhận: **{cach_nhan}**\n"
                    f" - <:TI_ultgift:1524096997815095359> Đặc quyền: {dac_quyen}\n"
                    f" - <:TI_ultcount:1524096758919991486> Sở hữu: `{so_nguoi}` người\n"
                ),
                color=role.color if role.color.value != 0 else 0xff73fa,
                timestamp=discord.utils.utcnow()
            )
            embed_role.set_thumbnail(url=bot_avatar_url)
            embed_role.set_footer(text=FOOTER_TEXT)

            await interaction.response.send_message(embed=embed_role, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())
            return

        # ====== KỊCH BẢN 2: MỞ SỔ TAY TỔNG HỢP (PHÂN TRANG) ======
        
        # Hàm tự động tạo khối văn bản cho từng role, không phải gõ tay nữa
        def get_role_block(role_id):
            info = ROLE_INFO_DB[role_id]
            emoji_prefix = EMOJI_EVENT if info["type"] == "event" else EMOJI_SPECIAL
            time_str = f"<t:{info['timestamp']}:D>" if info['timestamp'] else "Chưa cập nhật"
            
            return (
                f"## <@&{role_id}>\n"
                f" - Ra mắt: {time_str}\n"
                f" - {emoji_prefix} Cách nhận: **{info['cach_nhan']}**\n"
                f" - 🎁 Đặc quyền: {info['dac_quyen']}\n"
                f" - 👥 Sở hữu: `{count_role(role_id)}` người"
            )

        page_1 = """# 📘 SỔ TAY ROLE ĐẢO TUGLAR #
### ⚜️ Special Role ###
 Các role này thường chỉ dành cho một số người với các tiêu chí để nhận, đặc biệt hơn so với achievement role.

### 🎉 Event Role  ###
 - Các role này thường chỉ xuất hiện **1 lần duy nhất** với các sự kiện để đánh dấu lại cột mốc thời gian bạn đã đồng hành cùng với server."""

        # Bot tự động lấy data từ ROLE_INFO_DB để tạo trang, nhàn tênh!
        page_2 = f"""# 🎉 Event Role (Trang 1)
{get_role_block(1466299698800365695)}
{get_role_block(1274907870701424755)}
{get_role_block(1240597343049486397)}"""

        page_3 = f"""# 🎉 Event Role (Trang 2)
{get_role_block(1189375452603756645)}
{get_role_block(1157198996234842143)}
{get_role_block(1169623255297032272)}"""

        page_4 = f"""# ⚜️ Special Role
{get_role_block(1346173590642622528)}
{get_role_block(1175019718466359306)}
{get_role_block(1113018418300452894)}"""

        pages = [page_1, page_2, page_3, page_4]
        
        view = IndexPaginationView(pages, bot_avatar_url)
        embed_index = view.get_current_embed()

        await interaction.response.send_message(embed=embed_index, view=view, ephemeral=False, allowed_mentions=discord.AllowedMentions.none())

async def setup(bot):
    await bot.add_cog(IndexCog(bot))