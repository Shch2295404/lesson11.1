import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN, WEATHER_API_KEY

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функция получения прогноза погоды с повторными попытками в случае ошибки
async def fetch_weather(city: str, max_attempts: int = 3):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    for attempt in range(max_attempts):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        weather_desc = data['weather'][0]['description']
                        temperature = data['main']['temp']
                        feels_like = data['main']['feels_like']
                        return (f"🌦 Погода в {city}:\n"
                                f"☁️ Состояние: {weather_desc}\n"
                                f"🌡 Температура: {temperature}°C\n"
                                f"🥶 Ощущается как: {feels_like}°C")
                    else:
                        return f"⚠️ Ошибка получения данных. Проверьте название города. (Код ошибки: {response.status})"
        except aiohttp.ClientOSError as e:
            if attempt < max_attempts - 1:
                await asyncio.sleep(2)  # Ожидание перед новой попыткой
            else:
                return f"🔌 Ошибка соединения: {str(e)}. Попробуйте позже."

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer("👋 Привет! Я бот, который помогает узнать погоду.\n"
                         "🔹 Используйте /weather <город>, чтобы получить прогноз.")

# Обработчик команды /help
@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer("🆘 Список доступных команд:\n"
                         "/start - Запуск бота\n"
                         "/photo - Получить случайное изображение\n"
                         "/weather <город> - Узнать прогноз погоды\n"
                         "/help - Справка")

# Обработчик команды /photo
@dp.message(Command("photo"))
async def command_photo(message: Message):
    image_links = [
        "https://kartin.papik.pro/uploads/posts/2023-07/1689295122_kartin-papik-pro-p-kartinki-anomalii-pogodi-10.jpg",
        "https://kartin.papik.pro/uploads/posts/2023-07/1689295125_kartin-papik-pro-p-kartinki-anomalii-pogodi-19.jpg",
        "https://kartin.papik.pro/uploads/posts/2023-07/1689295133_kartin-papik-pro-p-kartinki-anomalii-pogodi-46.jpg",
        "https://kartin.papik.pro/uploads/posts/2023-07/1689295124_kartin-papik-pro-p-kartinki-anomalii-pogodi-18.jpg",
        "https://kartin.papik.pro/uploads/posts/2023-07/1689295127_kartin-papik-pro-p-kartinki-anomalii-pogodi-33.jpg"
    ]
    chosen_photo = random.choice(image_links)
    await message.answer_photo(photo=chosen_photo, caption="📸 Случайное изображение!")

# Обработчик команды /weather
@dp.message(Command("weather"))
async def command_weather(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❗ Укажите город. Пример: /weather Москва")
    else:
        city = args[1]
        weather_data = await fetch_weather(city)
        await message.answer(weather_data)

# Реакция на сообщение "Прогноз погоды"
@dp.message(F.text.lower() == "прогноз погоды")
async def weather_info(message: Message):
    await message.answer("🌍 Вы можете узнать погоду в любом городе! Просто отправьте команду:\n"
                         "`/weather <город>` (например: `/weather Санкт-Петербург`).")

# Ответ на отправку изображения
@dp.message(F.photo)
async def photo_reaction(message: Message):
    await message.answer("🎨 Отличный снимок! 😊")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
