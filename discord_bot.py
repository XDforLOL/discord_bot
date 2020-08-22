import discord
import logging
from datetime import datetime
import requests
import sys
import os
from discord import message
import coloredlogs

token = open("token.txt","r").readline()
client = discord.Client()
logger = logging.getLogger(__name__)
# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
coloredlogs.install(level='DEBUG')
LOGFILE = "chatlog.log"
current_time = datetime.now()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_member_join(member) -> str:
    channel = discord.utils.get(member.guild.text_channels, name="general")
    await channel.send(f"Hello There General {member.name}, Do not spam or i will delete the messages")


@client.event
async def on_message(message):
    if message.content.startswith('☁️ LastSeen'):
        req_author = find_last_message(message.content.replace('☁️ LastSeen ', ''))
        await message.channel.send(req_author)
    if message.content.startswith('☁️ Weather'):
        weather_city = weather_check(message.content.replace('☁️ Weather ', ''))
        await message.channel.send(weather_city)
    if is_spam(message):
        logging.info(f"I have deleted a message from {message.author}")
        await message.delete()
    else:
        logging.info("Message logged")
        log_message(message)


def log_message(message:message.Message, file_name:str=LOGFILE) -> str:
    with open(file_name, 'a', encoding="utf-8") as f:
        f.writelines("\n{}|{}|{}".format(current_time.strftime('%Y-%m-%d %H:%M:%S'), message.author, message.content.replace('\n ', '')))

# :cloud: LastSeen
def find_last_message(req_author):
    with open(LOGFILE, 'r', encoding="utf-8") as f:

        rows = f.readlines()
        len_list = len(rows)-1
        # range(len_list, 0, -1)
        for i in range(len_list, 0, -1):
            timestamp, author, content = rows[i].split("|")
            if req_author == author.split('#')[0]:
                seconds = (current_time - datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).total_seconds()
                return f'{author} last message {seconds:.2f} was seconds ago ;)'



def get_prior_from_file(file_name:str) -> str:
    with open(file_name, 'r', encoding="utf-8") as f:
        # file_content = f.readlines()
        # prior_row = file_content[-2]
        # timestamp, author, content = prior_row
        # if os.stat(file_name).st_size == 0:
        #     return
        # else:
        try:
            timestamp, author, content = f.readlines()[-1].split("|")
            return [ITEM.replace('\n', '') for ITEM in [author, content]]
        except IndexError:
            logger.warning(f'{file_name} is empty')




def is_spam(message:message.Message, file_name:str= "chatlog.log") -> bool:
    return get_prior_from_file(file_name) == (str(message.author), message.content)


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
