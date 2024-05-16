import telebot
import datetime
import sqlite3
class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.__create_table()
    def __create_table(self):
        sql = self.connect_db()
        sql["cursor"].execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_telegram NOT NULL UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                date_registration DATE,
                access BOOLEAN DEFAULT 1
            )
        ''')
        sql["cursor"].execute('''
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                date_send DATE,
                status BOOLEAN DEFAULT 0 CHECK(status IN (0, 1)),
                FOREIGN KEY (id_user) REFERENCES users(id)
            )
        ''')
        self.close(sql["cursor"], sql["connect"])
    def connect_db(self):
        with sqlite3.connect(self.db_name) as connect:
            cursor = connect.cursor()
        return {"connect": connect, "cursor": cursor}
    def check_user(self, user_id):
        sql = self.connect_db()
        sql["cursor"].execute('''
            SELECT * FROM users WHERE id_telegram = ?
        ''', (user_id, ))
        info_user = sql["cursor"].fetchone()
        print(info_user)
        self.close(sql["cursor"], sql["connect"])
        if info_user is None:
            return {
                "status": False
            }
        return {
            "status": True,
            "info_user": info_user
        }
    def create_user(self, message: dict):
        sql = self.connect_db()
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        sql["cursor"].execute('''
            INSERT INTO users (
                id_telegram, username, first_name, last_name, date_registration
            ) VALUES (?, ?, ?, ?, ?)
        ''',(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            date
        ))
        sql["connect"].commit()
        self.close(sql["cursor"], sql["connect"])
    def insert_message(self, message: dict):
        sql = self.connect_db()
        date = datetime.datetime.now().strftime("%Y-%m-%d")

        sql["cursor"].execute('''
            INSERT INTO messages (
                id_user, message_id, message_text, data_send
            ) VALUES (?, ?, ?, ?)
        ''', (
            
        ))
        self.close(sql["cursor"], sql["connect"])
    def close(self, cursor, connect):
        cursor.close()
        connect.close()
class TelegramBot(DataBase):
    def __init__(self, db_name, token):
        super().__init__(db_name) 
        self.bot = telebot.TeleBot(token)
        self.router()
    def router(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            # print(message)
            text = ""
            if self.check_user(message.from_user.id)["status"]:
                text += "С возвращением!"
            else:
                self.create_user(message)
                text += f"Добро пожаловать, {message.from_user.first_name}"
            self.bot.send_message(
                message.chat.id,
                text
                # f"Добро пожаловать, {message.from_user.first_name}!"
            )
        @self.bot.message_handler(func=lambda message: True)
        def echo_all(message):
            self.bot.reply_to(
                message,
                "Сообщение отправлено админу!"
            )
            # self.bot.delete_message(
            #     chat_id=message.chat.id,
            #     message_id=message.message_id
            # )
        self.bot.polling()
TelegramBot(
    db_name="tg.db",
    token="6892526091:AAGySZsP38Li8f0d5jzVofTeYLN6qhPFqJo"
)