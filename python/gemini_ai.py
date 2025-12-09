"""
Gemini AI 模組 - 智慧對話功能
生物機電工程概論 期末專題
"""

import google.generativeai as genai
from typing import Optional
import database as db
from config import GEMINI_API_KEY


# 系統提示詞
SYSTEM_PROMPT = """你是一個溫濕度監測系統的 AI 助手。你的任務是：
1. 回答用戶關於溫度、濕度、環境舒適度的問題
2. 根據感測器數據提供建議
3. 用繁體中文回答，語氣友善親切
4. 回答要簡潔，不要超過 200 字

你可以存取即時的溫濕度感測器數據。"""


class GeminiAI:
    """Gemini AI 助手"""
    
    def __init__(self):
        self.model = None
        self.enabled = False
        self._init_model()
    
    def _init_model(self):
        """初始化 Gemini 模型"""
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            print("[AI] Gemini API key not set, AI features disabled")
            return
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
            self.enabled = True
            print("[AI] Gemini AI initialized successfully")
        except Exception as e:
            print(f"[AI] Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def _get_sensor_context(self) -> str:
        """取得感測器數據上下文"""
        latest = db.get_latest_reading()
        stats = db.get_statistics(24)
        
        if not latest:
            return "目前沒有感測器數據。"
        
        context = f"""
目前感測器數據：
- 溫度：{latest['temperature']}°C
- 濕度：{latest['humidity']}%
- 體感溫度：{latest.get('heat_index', 'N/A')}°C
- 記錄時間：{latest['recorded_at']}

過去 24 小時統計：
- 平均溫度：{stats['temperature']['avg']}°C（最低 {stats['temperature']['min']}°C，最高 {stats['temperature']['max']}°C）
- 平均濕度：{stats['humidity']['avg']}%（最低 {stats['humidity']['min']}%，最高 {stats['humidity']['max']}%）
- 總記錄數：{stats['count']} 筆
"""
        return context
    
    async def chat(self, user_message: str) -> str:
        """
        與 AI 對話
        
        Args:
            user_message: 用戶訊息
            
        Returns:
            AI 回覆
        """
        if not self.enabled:
            return "AI 功能未啟用。請設定 GEMINI_API_KEY 環境變數。"
        
        try:
            # 組合完整提示
            sensor_context = self._get_sensor_context()
            full_prompt = f"""{SYSTEM_PROMPT}

{sensor_context}

用戶問題：{user_message}

請根據以上數據回答用戶的問題："""

            # 呼叫 Gemini API
            response = self.model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"[AI] Chat error: {e}")
            return f"AI 回覆失敗：{str(e)}"


# 全域 AI 實例
_ai_instance: Optional[GeminiAI] = None


def get_ai() -> GeminiAI:
    """取得 AI 實例（單例模式）"""
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = GeminiAI()
    return _ai_instance


async def chat(message: str) -> str:
    """快捷對話函數"""
    ai = get_ai()
    return await ai.chat(message)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=== Gemini AI Test ===")
        response = await chat("現在溫度如何？")
        print(f"Response: {response}")
    
    asyncio.run(test())
