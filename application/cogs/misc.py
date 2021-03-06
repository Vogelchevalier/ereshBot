import os
import re
import requests
import uuid
import xml.etree.ElementTree as elemTree
import discord
from discord.ext import commands
from discord import File
from application import BotState, commandLine, Auth

# TODO: deepfry image with Pillow https://pillow.readthedocs.io/en/stable/reference/ImageEnhance.html


class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rin',
                      description='The truth about Rin',
                      brief='The truth',
                      aliases=['eresh'])
    async def rin(self, ctx):
        await ctx.send("Ereshkigal > Ishtar > f/sn Rin > Loli Rin > f/ha Rin")

    @commands.command(name='dab',
                      description='Ereshkigal dabs',
                      brief='Eresh dabs')
    async def dab(self, ctx):
        await ctx.send(file=File('application/media/eresh-dab.png'))

    @commands.command(name='crab',
                      description='--crab <upper text>,<lower text>',
                      brief='Crabs')
    async def crab(self, ctx, *args):
        # TODO: subtitles instead of drawtext
        # TODO: line/underlined text
        # TODO: move to image/video manipulation cog
        msg = ''
        for i in range(len(args)):
            msg += args[i]
            msg += " "

        if len(msg.split(",")) != 2:
            await ctx.send("Give me 2 messages separated by a comma")
            return

        msg1 = re.sub(r'[\W_]+', ' ', msg[:-1].upper().split(",")[0])
        msg2 = re.sub(r'[\W_]+', ' ', msg[:-1].upper().split(",")[1])

        if len(msg1) > 40 or len(msg2) > 40:
            await ctx.send("Max message length 40 craracters. Cutting to size.")

        msg1 = msg1[:40]
        msg2 = msg2[:40]

        if len(msg1) == 0 and len(msg2) == 0:
            await ctx.send("Give me at least one message containing letters and/or numbers")
            return

        video = "application/media/crab3.mp4"
        font = "application/media/migu2m.ttf"
        max_f_size = "64"
        f_color = "white"

        max_text_width = 1080
        f_size = min(int(max_f_size), max_text_width // max(len(msg1), len(msg2)))

        salt = str(uuid.uuid4()).replace("-", "")[:5]
        output = f'{msg1}_{msg2}_{salt}.mp4'

        line_args1 = f'drawtext=fontfile={font}:text='
        line_args2 = f':fontcolor={f_color}:fontsize={f_size}:bordercolor=black:borderw=2:x=(w-text_w)/2:y=(h-text_h-text_h)/2'

        ffmpeg = ['ffmpeg', '-i', f'{video}', '-vf',
                  f'[in]{line_args1}{msg1}{line_args2},{line_args1}{msg2}{line_args2}+{f_size}[out]',
                  '-codec:a', 'copy', '-preset', 'veryfast', '-y', f'{output}']

        commandLine(ffmpeg)

        if os.path.exists(output):
            if os.path.getsize(output) > 1024:
                await ctx.send(file=File(output))
            else:
                await ctx.send("Something went wrong")

            os.remove(output)
        else:
            await ctx.send("Something went wrong")

    @commands.command(name='info',
                      description='Information about the bot and its status',
                      brief='Get the bot status and info')
    async def info(self, ctx):
        github_url = "https://github.com/Vogelchevalier/ereshBot"

        disabled_cogs = []
        enabled_cogs = []

        status_icons = {
            'online': ':green_circle:',
            'idle': ':yellow_circle:',
            'dnd': ':red_circle:'
        }

        for cog in BotState.STATUS['availableCogs']:
            if cog not in BotState.STATUS['disabledCogs']:
                enabled_cogs.append(cog[5:])
            else:
                disabled_cogs.append(cog[5:])

        author_icon = 'https://cdn.discordapp.com/avatars/459704067359244289/a120d9f0a972e15d9ac41a01ac28bcdb.png'

        status_message = ""

        if len(enabled_cogs) > 1:
            status_message += f'Enabled cogs\n'
            for cog in enabled_cogs:
                status_message += f'- **{cog}**\n'
            status_message = status_message[:-1]
            status_message += '\n'

        if len(disabled_cogs) > 0:
            status_message += '\n'
            status_message += f'Disabled cogs\n'
            for cog in disabled_cogs:
                status_message += f'- **{cog}**\n'
            status_message = status_message[:-1]
            status_message += '\n'

        status_message += '\n'
        status_message += 'See [COMMANDS.md](https://github.com/Vogelchevalier/ereshBot/blob/master/COMMANDS.md) or `--help` for commands'
        status_message += '\n\n'
        status_message += f'[GitHub]({github_url})'

        embed = discord.Embed(title='Vogelchevalier/ereshBot',
                              colour=discord.Colour.from_rgb(239, 183, 131))
        embed.set_footer(text=f'「地の女神、エレシュキガルが命じます！」')
        embed.set_author(name=BotState.STATUS['nickname'], icon_url=author_icon)
        embed.add_field(name=f'{status_icons.get(BotState.STATUS["onlineStatus"])} Playing {BotState.STATUS["playingStatus"]}', value=status_message, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='lastfm',
                      description='Gets the last played track from last.fm API for the provided user',
                      brief='Last.fm last played track',
                      aliases=['last', 'song', 'np'])
    async def lastfm(self, ctx, username='xLapin', mode='tiny'):

        if mode.lower() in ['full', 'verbose', 'detailed', 'detail']:
            mode = 'full'
        else:
            mode = 'tiny'

        api_url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1"

        key = Auth.LASTFM

        request_url = api_url + "&user=" + username + "&api_key=" + key

        response = requests.get(request_url)
        root = elemTree.fromstring(response.content)

        if not root[0]:
            await ctx.send("Something went wrong. Probably no user with that name.")
            return

        now_playing = root[0][0].get("nowplaying") == "true"
        artist = root[0][0][0].text
        song_title = root[0][0][1].text
        album = root[0][0][4].text
        song_url = root[0][0][5].text
        album_art = root[0][0][8].text
        album_art_large = root[0][0][9].text
        song_title_link = f'[{album}]({song_url})'
        lastfm_icon = 'http://icons.iconarchive.com/icons/sicons/basic-round-social/512/last.fm-icon.png'
        footer_text = f'Last.fm'

        if mode == 'tiny':
            embed = discord.Embed(title=song_title,
                                  colour=discord.Colour.from_rgb(239, 183, 131))
            embed.set_footer(text=album)
            embed.set_author(name=artist, icon_url=album_art)

            await ctx.send(embed=embed)

        elif mode == 'full':
            embed = discord.Embed(title=f'{artist}  -  {song_title}',
                                  colour=discord.Colour.from_rgb(239, 183, 131))
            embed.set_footer(icon_url=lastfm_icon, text=footer_text)
            embed.set_author(name=f'{username}{" is now playing " if now_playing else " last played "}')
            embed.set_image(url=album_art_large)
            embed.add_field(name='Album', value=song_title_link)

            await ctx.send(embed=embed)

        else:
            await ctx.send("Something went wrong")


def setup(bot):
    bot.add_cog(Misc(bot))
