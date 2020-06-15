import asyncio
import discord
from discord.ext import commands

def check_staff(config, roles):
    return any([role.name.lower() in config.staff for role in roles])


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._checker_chan = self.bot.config.checker_chan # clover channel (grab mentions)
        self.welcome_chan = self.bot.config.welcomer_chan # overflow (send welcome)
        self.welcome_message = self.bot.config.welcomer_message
        self.welcome_on = True
        self.timer = 3600
        self.loop = self.bot.loop.create_task(self.welcome_loop())

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if self.welcome_on and (ctx.channel.id == self._checker_chan):
            try:
                if 'clover' not in ctx.embeds[0].description.lower():
                    return
            except Exception:
                print('not a clover')
                return
            try:
                username = (ctx.embeds[0].description).split('<')[1].split('>')[0]
                username = ''.join([s for s in username if s.isdigit()])
                username = self.bot.get_user(int(username)).mention
            except Exception as e:
                print(f'Cannot find user: {e}')
                return
            try:
                channel = ctx.guild.get_channel(self.welcome_chan)
                msg = self.welcome_message.replace('$USER$', username)
                await channel.send(msg)
            except Exception as e:
                print(f'Error sending welcome: {e}')

    @commands.command(aliases=['changewelcome', 'changewelcomemessage'])
    async def change_welcome_message(self, ctx, *, msg):
        if not check_staff(self.bot.config, ctx.author.roles):
            return
        guild = ctx.guild
        if msg == '':
            msg = self.welcome_message.replace('$USER$', ctx.author.name)
            await ctx.channel.send(f"""***TESTING***
{msg}""")
            return
        msg = msg.replace('$SERVER$', guild.name)
        self.welcome_message = msg
        await ctx.channel.send(f"""***TESTING***
{msg}""")
        pass

    @commands.command(aliases=['changewelcomechannel'])
    async def change_welcome_channel(self, ctx, *, chan):
        if not check_staff(self.bot.config, ctx.author.roles):
            return
        chan = chan.strip(' ')
        if chan == '':
            return
        chan_id = str(filter(str.isdigit, chan))
        if chan_id == '':
            try:
                chan = [f for f in ctx.message.guild.channels if f.name.lower() == chan]
                if len(chan) == 0:
                    return
                chan_id = chan[0].id
            except Exception:
                return
        try:
            chan = ctx.message.guild.get_channel(chan_id)
            if not chan:
                return
        except Exception as e:
            return
        self.welcome_channel = chan.id
        await ctx.send(f'Welcome channel set to: {chan.mention}', delete_after=10)
        pass

    @commands.command(alias=['welcometimer'])
    async def welcome_timer(self, ctx, timer: int = 3600):
        if not check_staff(self.bot.config, ctx.author.roles):
            return
        self.timer = timer
        await ctx.send(f'Timer set to {timer}s', delete_after=10)
        pass

    @commands.command(alias=['welcometoggle'])
    async def toggle_welcomer(self, ctx, disable: bool = False):
        if not check_staff(self.bot.config, ctx.author.roles):
            return
        self.welcome_disable = disable
        self.welcome_on = ~self.welcome_on
        await ctx.send(f'Welcome message toggled: {self.welcome_on}')
        if not self.disable and not self.welcome_on and self.loop.done():
            self.loop = self.bot.loop.create_task(self.welcome_loop())
        pass

    async def welcome_loop(self):
        try:
            await self.bot.wait_until_ready()
        except Exception:
            return
        await self.__welcome_timer(self.timer)

    async def __welcome_checker(self):
        breaker = False
        while not breaker:
            breaker = self.welcome_on == True
        pass

    async def __welcome_sleep(self, time: int = 60):
        await asyncio.sleep(time)
        self.welcome_on = True
        pass

    async def __welcome_timer(self, time: int = 60):
        tasks = [self.__welcome_checker, self.__welcome_sleep(time)]
        f, uf = loop.run_until_complete(asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))
        pass


def setup(bot):
    bot.add_cog(Welcome(bot))
    print('Loaded Welcome')

