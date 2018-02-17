from .reseter import ClearConsole

def setup(bot):
	bot.add_cog(ClearConsole(bot))
