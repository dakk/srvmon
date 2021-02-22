import telegram

class TelegramNotifier:
    def __init__(self, token, chats):
        self.chats = chats
        self.bot = telegram.Bot(token=token)
    
    def sendMessage(self, msg):
        for x in self.chats:
            self.bot.sendMessage(chat_id=x, text=msg)

class Notifier:
    def __init__(self):
        pass