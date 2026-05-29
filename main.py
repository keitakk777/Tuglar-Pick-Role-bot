import discord
from discord.ext import commands
from keep_alive import keep_alive
from config import TOKEN

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

class TuglarBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    # Tự động tải thư mục Cogs khi bot khởi động
    async def setup_hook(self):
        await self.load_extension('cogs.booster')
        await self.tree.sync()
        print("🔄 Đã đồng bộ toàn bộ lệnh Slash (/) lên Server.")

    async def on_ready(self):
        print(f'✅ Bot {self.user} đã sẵn sàng hoạt động độc lập!')
        print('-------------------------------------------')

bot = TuglarBot()

if __name__ == '__main__':
    keep_alive() 
    bot.run(TOKEN)