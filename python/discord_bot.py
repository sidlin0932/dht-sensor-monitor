"""
Discord Bot 模組 - 互動指令
生物機電工程概論 期末專題
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import os
import asyncio
import io
import matplotlib
matplotlib.use('Agg')  # 使用非 GUI 後端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Optional

from config import DISCORD_BOT_TOKEN, BOT_COMMAND_PREFIX
import database as db
import gemini_ai


class SensorBot(commands.Bot):
    """感測器監控 Discord Bot"""
    

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=BOT_COMMAND_PREFIX,
            intents=intents,
            help_command=None  # 使用自訂的 help
        )
        
        self.last_reading: Optional[dict] = None
        self.arduino_reader = None  # 用於發送指令到 Arduino
        
        # 註冊指令
        self.add_commands()
    
    async def setup_hook(self):
        """Bot 啟動時的鉤子，用於同步指令"""
        # 從環境變數讀取 GUILD_ID（用於 guild-specific commands）
        guild_id = os.getenv('DISCORD_GUILD_ID')
        
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            print(f"[SYNC] Syncing Guild Commands (Guild ID: {guild_id})...")
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"[OK] Guild Commands synced!")
        else:
            print("[WARN] DISCORD_GUILD_ID not set, skipping command sync")
            print("       Tip: Set DISCORD_GUILD_ID to enable Guild Commands (instant effect)")
    
    def add_commands(self):
        """註冊所有指令"""
        
        @self.hybrid_command(name='help', aliases=['h', '幫助'], description="顯示幫助訊息")
        async def help_command(ctx):
            """顯示幫助訊息"""
            embed = discord.Embed(
                title="🤖 DHT 感測器 Bot 指令",
                description="支援 **Slash Command (/)** 與 **前綴指令 (!)**",
                color=0x00BFFF
            )
            
            commands_list = [
                (f"/now 或 {BOT_COMMAND_PREFIX}now", "查詢目前溫濕度"),
                (f"/history 或 {BOT_COMMAND_PREFIX}history [hours]", "查詢過去 N 小時數據"),
                (f"/stats 或 {BOT_COMMAND_PREFIX}stats [hours]", "查詢統計資料"),
                (f"/chart 或 {BOT_COMMAND_PREFIX}chart [hours]", "生成歷史圖表"),
                (f"/status 或 {BOT_COMMAND_PREFIX}status", "查詢系統狀態"),
                (f"/buzz 或 {BOT_COMMAND_PREFIX}buzz", "🔔 手動觸發蜂鳴器警報"),
                (f"/ai 或 {BOT_COMMAND_PREFIX}ai [問題]", "與 AI 助手對話"),
                (f"/help 或 {BOT_COMMAND_PREFIX}help", "顯示此幫助訊息"),
            ]
            
            for cmd, desc in commands_list:
                embed.add_field(name=cmd, value=desc, inline=False)
            
            # 自動警報說明
            embed.add_field(
                name="\n⚠️ 自動警報觸發條件",
                value="當以下情況發生時，Arduino 蜂鳴器會自動響起：\n"
                      "🔴 **溫度過高**: > 35°C\n"
                      "🔵 **溫度過低**: < 15°C\n"
                      "💧 **濕度過高**: > 85%\n"
                      "🏜️ **濕度過低**: < 20%",
                inline=False
            )
            
            # RGB LED 說明
            embed.add_field(
                name="\n💡 RGB LED 燈號說明",
                value="🟢 **綠色**: 溫度 20-28°C 且 濕度 40-70% (舒適)\n"
                      "🔵 **藍色**: 溫濕度在正常範圍 (一般)\n"
                      "🔴 **紅色**: 溫度 <15°C 或 >35°C，或濕度 <20% 或 >85% (警報)",
                inline=False
            )
            
            embed.set_footer(text="生物機電工程概論 期末專題")
            await ctx.send(embed=embed)
        
        @self.hybrid_command(name='now', aliases=['n', '現在', '目前'], description="查詢目前溫濕度")
        async def now_command(ctx):
            """查詢目前溫濕度"""
            # Defer response if interaction (slash command) takes time, though DB lookup is fast
            if ctx.interaction:
                await ctx.defer()

            reading = db.get_latest_reading()
            
            if not reading:
                await ctx.send("❌ 目前沒有數據，請確認感測器是否正常運作")
                return
            
            # 計算時間差
            recorded_at = datetime.fromisoformat(str(reading['recorded_at']))
            time_diff = datetime.now() - recorded_at
            minutes_ago = int(time_diff.total_seconds() / 60)
            
            embed = discord.Embed(
                title="🌡️ 目前溫濕度",
                color=0x00FF00 if minutes_ago < 5 else 0xFFFF00
            )
            
            embed.add_field(
                name="🌡️ 溫度",
                value=f"**{reading['temperature']:.1f}°C**",
                inline=True
            )
            embed.add_field(
                name="💧 濕度",
                value=f"**{reading['humidity']:.1f}%**",
                inline=True
            )
            
            if reading.get('heat_index'):
                embed.add_field(
                    name="🔥 體感溫度",
                    value=f"**{reading['heat_index']:.1f}°C**",
                    inline=True
                )
            
            embed.set_footer(text=f"更新於 {minutes_ago} 分鐘前")
            
            await ctx.send(embed=embed)
        
        @self.hybrid_command(name='history', aliases=['hist', '歷史'], description="查詢過去 N 小時數據")
        @app_commands.describe(hours="查詢的小時數 (預設 24)")
        async def history_command(ctx, hours: int = 24):
            """查詢歷史數據"""
            if ctx.interaction:
                await ctx.defer()

            if hours < 1:
                hours = 1
            elif hours > 168:  # 最多 7 天
                hours = 168
            
            readings = db.get_readings_by_hours(hours)
            
            if not readings:
                await ctx.send(f"❌ 過去 {hours} 小時沒有數據")
                return
            
            # 取最近 10 筆顯示
            recent = readings[-10:]
            
            embed = discord.Embed(
                title=f"📜 過去 {hours} 小時歷史數據",
                description=f"共 {len(readings)} 筆記錄，顯示最近 {len(recent)} 筆",
                color=0x00BFFF
            )
            
            history_text = ""
            for reading in recent:
                recorded_at = datetime.fromisoformat(str(reading['recorded_at']))
                time_str = recorded_at.strftime("%H:%M")
                history_text += f"`{time_str}` 🌡️ {reading['temperature']:.1f}°C 💧 {reading['humidity']:.1f}%\n"
            
            embed.add_field(name="最近記錄", value=history_text, inline=False)
            
            await ctx.send(embed=embed)
        
        @self.hybrid_command(name='stats', aliases=['統計'], description="查詢統計資料")
        @app_commands.describe(hours="查詢的小時數 (預設 24)")
        async def stats_command(ctx, hours: int = 24):
            """查詢統計資料"""
            if ctx.interaction:
                await ctx.defer()
                
            if hours < 1:
                hours = 1
            elif hours > 168:
                hours = 168
            
            stats = db.get_statistics(hours)
            
            if stats['count'] == 0:
                await ctx.send(f"❌ 過去 {hours} 小時沒有數據")
                return
            
            embed = discord.Embed(
                title=f"📊 過去 {hours} 小時統計",
                description=f"共 {stats['count']} 筆數據",
                color=0x9932CC
            )
            
            temp = stats['temperature']
            embed.add_field(
                name="🌡️ 溫度統計",
                value=f"平均: **{temp['avg']}°C**\n最低: {temp['min']}°C\n最高: {temp['max']}°C",
                inline=True
            )
            
            hum = stats['humidity']
            embed.add_field(
                name="💧 濕度統計",
                value=f"平均: **{hum['avg']}%**\n最低: {hum['min']}%\n最高: {hum['max']}%",
                inline=True
            )
            
            await ctx.send(embed=embed)
        
        @self.hybrid_command(name='chart', aliases=['圖表', 'graph'], description="生成歷史圖表")
        @app_commands.describe(hours="查詢的小時數 (預設 6)")
        async def chart_command(ctx, hours: int = 6):
            """生成歷史圖表"""
            if ctx.interaction:
                await ctx.defer()

            if hours < 1:
                hours = 1
            elif hours > 48:
                hours = 48
            
            readings = db.get_readings_by_hours(hours)
            
            if len(readings) < 2:
                await ctx.send(f"❌ 數據不足，無法生成圖表（需要至少 2 筆數據）")
                return
            
            # 準備數據
            times = [datetime.fromisoformat(str(r['recorded_at'])) for r in readings]
            temps = [r['temperature'] for r in readings]
            humids = [r['humidity'] for r in readings]
            
            # 建立圖表
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
            fig.suptitle(f'過去 {hours} 小時溫濕度變化', fontsize=14, fontweight='bold')
            
            # 設定中文字體
            plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 溫度圖
            ax1.plot(times, temps, 'r-o', linewidth=2, markersize=4, label='溫度')
            ax1.fill_between(times, temps, alpha=0.3, color='red')
            ax1.set_ylabel('溫度 (°C)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='upper right')
            
            # 濕度圖
            ax2.plot(times, humids, 'b-o', linewidth=2, markersize=4, label='濕度')
            ax2.fill_between(times, humids, alpha=0.3, color='blue')
            ax2.set_ylabel('濕度 (%)', fontsize=12)
            ax2.set_xlabel('時間', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='upper right')
            
            # 格式化 X 軸時間
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 儲存到記憶體
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            # 發送圖片
            file = discord.File(buf, filename='chart.png')
            
            embed = discord.Embed(
                title=f"📈 過去 {hours} 小時溫濕度圖表",
                description=f"共 {len(readings)} 筆數據",
                color=0x00FF00
            )
            embed.set_image(url="attachment://chart.png")
            
            await ctx.send(embed=embed, file=file)
        
        @self.hybrid_command(name='status', aliases=['狀態'], description="查詢系統狀態")
        async def status_command(ctx):
            """查詢系統狀態"""
            if ctx.interaction:
                await ctx.defer()
                
            total_count = db.get_reading_count()
            latest = db.get_latest_reading()
            
            embed = discord.Embed(
                title="⚙️ 系統狀態",
                color=0x00FF00
            )
            
            embed.add_field(
                name="📊 總記錄數",
                value=f"**{total_count}** 筆",
                inline=True
            )
            
            if latest:
                recorded_at = datetime.fromisoformat(str(latest['recorded_at']))
                time_diff = datetime.now() - recorded_at
                minutes_ago = int(time_diff.total_seconds() / 60)
                
                status = "🟢 正常" if minutes_ago < 5 else "🟡 延遲" if minutes_ago < 15 else "🔴 離線"
                
                embed.add_field(
                    name="📡 感測器狀態",
                    value=status,
                    inline=True
                )
                
                embed.add_field(
                    name="🕐 最後更新",
                    value=f"{minutes_ago} 分鐘前",
                    inline=True
                )
            
            embed.set_footer(text="DHT 感測器監測系統")
            
            await ctx.send(embed=embed)
        
        @self.hybrid_command(name='buzz', aliases=['蜂鳴', '警報', 'alarm'], description="手動觸發蜂鳴器警報")
        async def buzz_command(ctx):
            """手動觸發蜂鳴器警報"""
            if ctx.interaction:
                await ctx.defer()
            
            # 檢查是否有 Arduino 連接
            if self.arduino_reader is None:
                embed = discord.Embed(
                    title="⚠️ 無法觸發蜂鳴器",
                    description="Arduino 未連接或系統處於模擬模式。\n請確認 Arduino 已連接到電腦。",
                    color=0xFFCC00
                )
                await ctx.send(embed=embed)
                return
            
            # 發送指令到 Arduino
            try:
                success = self.arduino_reader.send_command("BUZZ")
                
                if success:
                    embed = discord.Embed(
                        title="🔔 蜂鳴器已觸發!",
                        description="已成功獲送指令到 Arduino，蜂鳴器應該正在響起！",
                        color=0xFF6600
                    )
                    embed.add_field(
                        name="⚠️ 自動警報條件",
                        value="• 溫度 > 35°C 或 < 15°C\n• 濕度 > 85% 或 < 20%",
                        inline=False
                    )
                else:
                    embed = discord.Embed(
                        title="❌ 發送失敗",
                        description="無法發送指令到 Arduino，請檢查連接狀態。",
                        color=0xFF0000
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ 觸發蜂鳴器失敗：{str(e)}")
        
        @self.hybrid_command(name='ai', aliases=['問', 'ask'], description="與 AI 助手對話")
        @app_commands.describe(question="你想問的問題")
        async def ai_command(ctx, *, question: str = None):
            """與 AI 助手對話"""
            if ctx.interaction:
                await ctx.defer()
            
            if not question:
                await ctx.send("請提供問題！例如：`!ai 現在溫度如何？`")
                return
            
            # 檢查 AI 是否啟用
            ai = gemini_ai.get_ai()
            if not ai.enabled:
                embed = discord.Embed(
                    title="AI 功能未啟用",
                    description="請設定 GEMINI_API_KEY 環境變數以啟用 AI 功能。\n\n"
                                "取得 API Key: https://aistudio.google.com/app/apikey",
                    color=0xFFCC00
                )
                await ctx.send(embed=embed)
                return
            
            # 呼叫 AI
            try:
                response = await ai.chat(question)
                
                # 限制回覆長度
                if len(response) > 1900:
                    response = response[:1900] + "..."
                
                embed = discord.Embed(
                    title="🤖 AI 助手回覆",
                    description=response,
                    color=0x9932CC
                )
                embed.set_footer(text=f"問題：{question[:50]}...")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"AI 回覆失敗：{str(e)}")
        
        @self.hybrid_command(name='setcolor', aliases=['顏色', 'color'], description="🎨 設定 RGB LED 顏色")
        @app_commands.describe(r="紅色 (0-255)", g="綠色 (0-255)", b="藍色 (0-255)")
        async def setcolor_command(ctx, r: int, g: int, b: int):
            """設定 RGB LED 顏色"""
            if ctx.interaction:
                await ctx.defer()
            
            # 驗證範圍
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # 檢查是否有 Arduino 連接
            if self.arduino_reader is None:
                embed = discord.Embed(
                    title="⚠️ 無法設定顏色",
                    description="Arduino 未連接或系統處於模擬模式。",
                    color=0xFFCC00
                )
                await ctx.send(embed=embed)
                return
            
            # 發送指令到 Arduino
            try:
                success = self.arduino_reader.send_command(f"SET_COLOR:{r},{g},{b}")
                
                if success:
                    # 計算顏色的 hex 值以顯示
                    color_hex = (r << 16) | (g << 8) | b
                    embed = discord.Embed(
                        title="🎨 LED 顏色已設定!",
                        description=f"RGB ({r}, {g}, {b})",
                        color=color_hex
                    )
                    embed.add_field(name="💡 提示", value="使用 `/autocolor` 可切回自動模式", inline=False)
                else:
                    embed = discord.Embed(
                        title="❌ 發送失敗",
                        description="無法發送指令到 Arduino。",
                        color=0xFF0000
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ 設定顏色失敗：{str(e)}")
        
        @self.hybrid_command(name='autocolor', aliases=['自動顏色', 'auto'], description="🔄 切回自動 LED 模式")
        async def autocolor_command(ctx):
            """切回自動 LED 模式"""
            if ctx.interaction:
                await ctx.defer()
            
            if self.arduino_reader is None:
                embed = discord.Embed(
                    title="⚠️ 無法切換模式",
                    description="Arduino 未連接或系統處於模擬模式。",
                    color=0xFFCC00
                )
                await ctx.send(embed=embed)
                return
            
            try:
                success = self.arduino_reader.send_command("AUTO_COLOR")
                
                if success:
                    embed = discord.Embed(
                        title="🔄 已切回自動模式",
                        description="LED 將根據環境品質自動變色\n🟢 良好 → 🔵 普通 → 🔴 警報",
                        color=0x00FF00
                    )
                else:
                    embed = discord.Embed(
                        title="❌ 發送失敗",
                        description="無法發送指令到 Arduino。",
                        color=0xFF0000
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ 切換失敗：{str(e)}")
        
        @self.hybrid_command(name='setbuzzer', aliases=['蜂鳴器', 'buzzer'], description="🔔 觸發蜂鳴器指定次數")
        @app_commands.describe(times="響鈴次數 (1-10)")
        async def setbuzzer_command(ctx, times: int = 3):
            """觸發蜂鳴器指定次數"""
            if ctx.interaction:
                await ctx.defer()
            
            # 驗證範圍
            times = max(1, min(10, times))
            
            if self.arduino_reader is None:
                embed = discord.Embed(
                    title="⚠️ 無法觸發蜂鳴器",
                    description="Arduino 未連接或系統處於模擬模式。",
                    color=0xFFCC00
                )
                await ctx.send(embed=embed)
                return
            
            try:
                success = self.arduino_reader.send_command(f"SET_BUZZER:{times}")
                
                if success:
                    embed = discord.Embed(
                        title="🔔 蜂鳴器已觸發!",
                        description=f"響鈴次數：**{times}** 次",
                        color=0xFF6600
                    )
                else:
                    embed = discord.Embed(
                        title="❌ 發送失敗",
                        description="無法發送指令到 Arduino。",
                        color=0xFF0000
                    )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ 觸發蜂鳴器失敗：{str(e)}")
    
    async def on_ready(self):
        """Bot 啟動完成"""
        print(f"[BOT] Discord Bot online: {self.user.name}")
        print(f"[INFO] Command prefix: {BOT_COMMAND_PREFIX}")
    
    def update_last_reading(self, reading: dict):
        """更新最後一筆讀數（供外部呼叫）"""
        self.last_reading = reading
    
    def set_arduino_reader(self, reader):
        """設定 Arduino Reader 參考（供外部呼叫）"""
        self.arduino_reader = reader


def run_bot():
    """執行 Discord Bot"""
    if DISCORD_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[WARN] Please set DISCORD_BOT_TOKEN in config.py")
        return
    
    bot = SensorBot()
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    print("=== Discord Bot 測試 ===")
    run_bot()
