import discord
import requests
import json
import urllib.request
import re
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import youtube_dl
import random

import config

client = commands.Bot(command_prefix = "|")
players = {}

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    # Apex legends stats
    elif message.content.startswith('!stats'):

        inp = message.content
        player_name = inp[7:]

        header = {'TRN-Api-Key' : config.api_key_apex}

        url = "https://public-api.tracker.gg/apex/v1/standard/profile/5/"
        url = url + player_name
  
        msg = ""
        try:
            req_list = requests.get(url, headers=header)
            pars = json.loads(req_list.content)
            msg = player_name + "'s stats:\n"
            msg = msg + "Level: " + pars['data']['stats'][0]['displayValue'] + "\n"
            msg = msg + "Main Legend: " + pars["data"]["children"][0]["metadata"]["legend_name"]+ "\n"
            msg = msg + "Kills: " + pars['data']['children'][0]['stats'][0]['displayValue'] + "\n"

        except:
            msg = player_name + " has no stats\n"

        await client.send_message(message.channel, msg)

    # league stats
    elif message.content.startswith('!lol'):
        key = config.api_key_league
        inp = message.content
        player_name = inp[5:]

        url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        url = url + player_name + "?"
        url = url + "api_key=" + key
        #print(url)
        url2 = "https://na1.api.riotgames.com/lol/league/v4/positions/by-summoner/"

        url4 = "http://ddragon.leagueoflegends.com/cdn/6.24.1/data/en_US/champion.json"
        req_champs = requests.get(url4)
        parsed_champs = json.loads(req_champs.content)

        msg = ""
        try:
            # get encryped id
            req_list = requests.get(url)
            pars = json.loads(req_list.content)
            encryped_id = pars['id']
            account_id = pars['accountId']

            # new get req with encrypted id
            url2 = url2 + encryped_id + "?"
            url2 = url2 + "api_key=" + key
            print(url2)
            req_list = requests.get(url2)
            parss = json.loads(req_list.content)

            # parse through / grab values
            league = parss[0]['tier']
            rank = parss[0]['rank']
            wins = str(parss[0]['wins'])
            losses = str(parss[0]['losses'])
            lp = str(parss[0]['leaguePoints'])
            position = parss[0]['position']

            if position == "UTILITY":
                position = "SUPPORT"

            # structure outgoing message
            msg = msg + player_name + ":\n" 
            msg = msg + "   " + league + ": " + rank + "\n"
            msg = msg + "   " + lp + " league points\n"
            msg = msg + "   Wins: " + wins + "\n"
            msg = msg + "   Losses: " + losses + "\n"
            msg = msg + "   " + position + " main\n\n"

            # get req match history(last three games)
            url3 = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
        
            url3 = url3 + account_id + "?"
            url3 = url3 + "api_key=" + key
            url3 = url3 + "&endIndex=3"
            req_list = requests.get(url3)
            parss = json.loads(req_list.content)
            
            # add match id and champ id to list
            game_id_list = []
            for game in parss['matches']:
                match_list = []
                match_list.append(game['gameId'])
                match_list.append(game['champion'])
                game_id_list.append(match_list)


            
            msg = msg + "Last 3 games:\n"
            for match in game_id_list:
                url3 = "https://na1.api.riotgames.com/lol/match/v4/matches/"
                url3 = url3 + str(match[0]) + "?"
                url3 = url3 + "api_key=" + key
                req_list = requests.get(url3)
                parsed = json.loads(req_list.content)

                champion_name = []
                for p_champs, p_value in parsed_champs['data'].items():
                    is_correct_id = False
                    for p_key, p_val in p_value.items():
                        if p_key == "key":
                            if p_val == str(match[1]):
                                is_correct_id = True
                        else:
                            if is_correct_id:
                                champion_name.append(p_val)
                                is_correct_id = False

                count = 0
                for champs in parsed['participants']:
                    if champs['championId'] == match[1]:
                        msg = msg + "   " + champion_name[count]
                        msg = msg + "   kills: " + str(champs['stats']['kills']) 
                        msg = msg + "   deaths: " + str(champs['stats']['deaths']) 
                        msg = msg + "   Game "
                        if champs['stats']['win'] is True:
                            msg = msg + "Won\n"
                        else:
                            msg = msg + "Lost\n"
                        count = count + 1

        except:
            # player not found
            msg = player_name + " has no stats\n"

        await client.send_message(message.channel, msg)

    # Dancing dog gif
    elif message.content.startswith('!dance'):
        dance = []
        dance.append("https://media.tenor.com/images/3b5aea40a2c8500afbdd4544489d2a24/tenor.gif")
        dance.append("https://giphy.com/gifs/snl-3o7TKLzYbpcEJbKYik")
        dance.append("https://tenor.com/view/worried-kermit-kermit-the-frog-muppets-stress-gif-7121337")
        dance.append("https://tenor.com/view/dancing-baby-fat-happy-dance-gif-12413299")
        dance.append("https://tenor.com/view/dance-dancing-happy-smile-excited-gif-5043292")
        dance.append("https://giphy.com/gifs/funny-dance-3IP8R5HQch7Rm")
        dance.append("https://giphy.com/gifs/cat-funny-WXB88TeARFVvi")
        #dance.append("")

        msg = random.choice(dance)
        await client.send_message(message.channel, msg)      

    elif message.content.startswith('!'):
        msg = "Usage error: " + message.content + " is not an acceptable command\n"
        msg = msg + "Try !hello or !stats_playername"
        await client.send_message(message.channel, msg)

    await client.process_commands(message)

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

@client.command(pass_context=True)
async def play(ctx, song):
    await client.say("Playing: " + song)
    song_name = song + " song"
    query = urllib.parse.quote(song_name)
    url = "http://www.youtube.com/results?search_query="+query
    response = urllib.request.urlopen(url)
    html = response.read()
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html.decode())
    urls = "https://www.youtube.com/watch/" + search_results[0]

    channel = ctx.message.author.voice.voice_channel
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    #url = 'https://youtu.be/LiaYDPRedWQ'

    #beforeArgs = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    #player = await voice_client.create_ytdl_player(url=urls, ytdl_options=self.ytdl_format_options, before_options=beforeArgs)
    player = await voice_client.create_ytdl_player(urls)
    players[server.id] = player
    player.start()

@client.command(pass_context=True)
async def stop(ctx):
    idx = ctx.message.server.id
    players[idx].stop()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

# real server
client.run('NTQ4MjkxNTY3MDEwNDQ3Mzk3.D1DMCA.9mgXmgi0ulQi5PyKhwsBSSWapYs')

# test server
#client.run('NTQ4Mjc1Mjk3MTY3MDgxNDkx.D1DN8A.81xhhgHuM4R2RLSGGJ99C0cdk3s')