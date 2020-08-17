import discord
import logging
import datetime
import requests
import sys
from discord import message


token = open("token.txt","r").readline()
client = discord.Client()
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_member_join(member) -> str:
    channel = discord.utils.get(member.guild.text_channels, name="general")
    await channel.send(f"Hello There General {member.name}, Do not spam or i will delete the messages")


@client.event
async def on_message(message):
    log_message(message)
    if message.content.startswith('☁️ Weather'):
        city = weather_check(message.content.replace('☁️ Weather ', ''))
        await message.channel.send(city)
    if is_spam(message):
        logging.info(f"I have deleted a message from {message.author}")
        await message.delete()
    else:
        logging.info("Message logged")


def log_message(message:message.Message, file_name:str="chatlog.log"):
    current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with open(file_name, 'a', encoding="utf-8") as f:
        f.writelines("\n{}|{}|{}".format(current_time, message.author, message.content.replace('\n ', '')))


def get_prior_from_file(file_name:str) -> str:
    with open(file_name, 'r', encoding="utf-8") as f:
        # file_content = f.readlines()
        # prior_row = file_content[-2]
        # timestamp, author, content = prior_row
        timestamp, author, content = f.readlines()[-2].split("|")
        return [ITEM.replace('\n', '') for ITEM in [author, content]]


def is_spam(message:message.Message, file_name:str= "chatlog.log") -> bool:
    return get_prior_from_file(file_name) == str(message.author), message.content


def weather_check(city_name:str) -> str:
    api_key = "d3c0bad728a9a93bc76d2bb8fb061b4e"
    base_url = "https://api.openweathermap.org/data/2.5/weather?q="
    #todo f strings
    response_json = requests.get(base_url + city_name + "&appid=" + api_key).json()

    if response_json["cod"] != "404":
        relavent_part = response_json["main"]
        current_temperature = relavent_part['temp'] - 273
        current_pressure = relavent_part["pressure"]
        current_humidiy = relavent_part["humidity"]

        weather_part_json = response_json["weather"]
        weather_description = weather_part_json[0]["description"]

        return(
            f""" Temperature (in celcius unit) ={current_temperature}
            atmospheric pressure (in hPa unit) = {current_pressure}
            humidity (in percentage) = {current_humidiy}
            description = {weather_description}"""
        )
    else:
        # print(" City Not Found ")
        raise ValueError("City not found")





if __name__ == '__main__':
    client.run(token)
