
import logging
import os
import traceback
from discord_webhook import DiscordWebhook, DiscordEmbed

class DiscordWebhookHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def emit(self, record):
        if not self.webhook_url:
            return

        try:
            # 建立一個 webhook
            webhook = DiscordWebhook(url=self.webhook_url)

            # 建立一個嵌入式訊息
            if record.levelno >= logging.ERROR:
                title = f"❌ Backend Error: {record.levelname}"
                color = "E74C3C" # 紅色
            else:
                title = f"ℹ️ Backend Info: {record.levelname}"
                color = "3498DB" # 藍色

            description = f"""**Message:**
{record.getMessage()}

"""

            # 如果有例外訊息，加入 traceback
            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
                
                # Take the last 10 lines of the traceback
                truncated_tb_list = tb_list[-10:]
                tb_str = "".join(truncated_tb_list)

                # Add a message if the traceback was truncated
                if len(tb_list) > 10:
                    tb_str = "(Traceback truncated - showing last 10 lines)\n" + tb_str

                # Apply the character limit for Discord
                if len(tb_str) > 1800:
                    tb_str = tb_str[:1790] + "...\n(Further truncated due to Discord limit)"

                description += f"""**Traceback:**
```python
{tb_str}
```"""


            embed = DiscordEmbed(
                title=title,
                description=description,
                color=color
            )
            
            embed.set_timestamp()

            webhook.add_embed(embed)
            response = webhook.execute()

        except Exception as e:
            # 如果發送到 Discord 時出錯，打印到控制台
            print(f"Error sending log to Discord: {e}")
            print(f"Original log record: {self.format(record)}")

