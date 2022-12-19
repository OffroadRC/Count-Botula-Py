# Count Botula

import os
import os.path
from pickle import TRUE
import random
import interactions
import mysql.connector
import ast
from asyncio.windows_events import NULL
import operator as op
import discord
import inspect
from math import sqrt
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PATH = os.getenv("ROW_PATH")
DBHOST = os.getenv("DB_HOST")
DBUSER = os.getenv("DB_USER")
DBPASS = os.getenv("DB_PASS")
DBNAME = os.getenv("DB_NAME")

SD_ROLE_ADMIN = 960654967067275324
SD_CHANNEL_STAFFCHAT = 961845074629648455
SD_CHANNEL_CURSING = 961847931571437588
SD_CHANNEL_COUNTING = 977459615283417099
SETTINGS_TABLE_PREFIX = "settings_"
CMD_PREFIX = '/'
EMOJI_CHECKMARK = '✅'
EMOJI_X = '❌'
EMOJI_STAR = '⭐'

intents = discord.Intents(messages=True, guilds=True)
intents.reactions = True
bot = interactions.Client(token=TOKEN)


# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
			 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
			 ast.USub: op.neg}


def Math(expression):
	try:
		solution = eval_expr(expression)
	except:
		return 1, "Hmm...something went wrong."
	else:
		print(f"expression = {expression}")
		print(f"solution = {solution}")
		return 0, solution


# Math
def eval_expr(expr):
	print("eval_expr:")
	return eval_(ast.parse(expr, mode='eval').body)


# Math
def eval_(node):
	print("eval_:")
	if isinstance(node, ast.Num): # <number>
		print(f"node.n = {node.n}")
		return node.n
	elif isinstance(node, ast.BinOp): # <left> <operator> <right>
		print(f"operators[type(node.op)](eval_(node.left), eval_(node.right)) = {operators[type(node.op)](eval_(node.left), eval_(node.right))}")
		return operators[type(node.op)](eval_(node.left), eval_(node.right))
	elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
		print(f"operators[type(node.op)](eval_(node.operand)) = {operators[type(node.op)](eval_(node.operand))}")
		return operators[type(node.op)](eval_(node.operand))
	else:
		raise TypeError(node)


@bot.command(name="count",
			 description="Counting!",
			 options=[
				 interactions.Option(
					 name="operation",
					 description="What would you like to do?",
					 type=interactions.OptionType.STRING,
					 required=True,
					 choices=[
						 interactions.Choice(name="start", value="start"),
						 interactions.Choice(name="stop", value="stop"),
						 interactions.Choice(name="pause", value="pause"),
						 interactions.Choice(name="restart", value="restart"),
						 interactions.Choice(name="help", value="help")
					 ]
				 ),
			 ])
async def count(ctx: interactions.CommandContext, operation: str):
	server_id = ctx.guild.id
	print(f"Connecting to database '{DBNAME}'...")
	db = mysql.connector.connect(host=DBHOST,
								 user=DBUSER,
								 password=DBPASS,
								 database=DBNAME)
	print(f"Operation '{operation}' requested.")

	if operation == "start":
		countNum = 0
		member = NULL
		isRunning = 1
		highScore = 0
		query = f"INSERT INTO counting (ServerID, LastNum, LastMember, IsRunning, HighScore)" \
			f"VALUES('{server_id}', '{countNum}', '{member}', '{isRunning}', '{highScore}')" \
			f"ON DUPLICATE KEY UPDATE LastNum='{countNum}', LastMember='{member}', IsRunning='{isRunning}'"
		descText = "A new count has been started!"
		await ctx.send(embeds=interactions.Embed(title="1...2...5!", description=descText))
		await ctx.send("0")

	if operation == "stop":
		countNum = 0
		member = NULL
		isRunning = 0
		highScore = NULL
		query = f"UPDATE counting SET LastNum='{countNum}', LastMember='{member}', IsRunning='{isRunning}'" \
			f"WHERE ServerID='{server_id}'"

	if operation == "pause":
		countNum = 0
		member = NULL
		isRunning = 0
		highScore = NULL
		query = f"UPDATE counting SET IsRunning='{isRunning}'" \
			f"WHERE ServerID='{server_id}'"

	if operation == "restart":
		countNum = 0
		member = NULL
		isRunning = 1
		highScore = NULL
		query = f"UPDATE counting SET LastNum='{countNum}', LastMember='{member}', IsRunning='{isRunning}'" \
			f"WHERE ServerID='{server_id}'"

	if operation == "help":
		descText = \
			  "*Commands*\n"\
			 f"Usage: `{CMD_PREFIX}count [command]`\n"\
			  "`start`		- Starts a new count if one is not already in progress.\n"\
			  "`pause`		- Pauses the count so that `=` can be used safely without affecting count progress.\n"\
			  "`stop`		- Resets the count without automatically starting a new count.\n"\
			  "`restart`	- Resets the count and starts a new one.  Can also be used like `start`.\n"\
			  "`help`		- You are here. (Default)\n\n"\
			  \
			  "Begin messages with `=` to enter an expression to solve.  Can also be used as a calculator outside of counting!\n"\
			  "Example: `= 3*3`\n"\
			  "*Supported operations:*\n"\
			  "`+`			- Addition			`0+9`\n"\
			  "`-`			- Subtraction		`10-1`\n"\
			  "`*`			- Multiplication	`3*3`\n"\
			  "`/`			- Division			`27/3`\n"\
			  "`()`			- Parentheses		`(6-3)*3`\n"\
			  "`**`			- Exponent			`3**2`		Exponent of 0.5 gives square root: `81**0.5`\n"
		await ctx.send(embeds=interactions.Embed(title="Help", description=descText))

	else:
		c = db.cursor()
		c.execute(query)
		c.close()


@bot.event
async def on_message(message: discord.Message):
	print(f"{inspect.currentframe().f_code.co_name}")
	print(f"message:\n{message.content}")
	print(f"user:\n{message.author} {message.author.id}")
	channelCounting = bot.get_channel(SD_CHANNEL_COUNTING)
	channelFrom = message.channel

	if message.author != bot.user:
		if message.content.startswith('='):
			strippedMessage = message.content.strip("= ")
			code, output = Math(strippedMessage)
			if channelFrom == channelCounting: # counting
				if code == 0: # no errors
					serverID = channelFrom.guild.id
					countData = GetCount(serverID)
					print(f"countData = {countData}")
					if countData == []:
						await channelFrom.send(f"No count record exists for this server yet!  Use `{CMD_PREFIX}count start` to start one.")
					else:
						isRunning = countData[2]
						if isRunning:
							lastNum = countData[0]
							nextNum = lastNum + 1
							lastMember = countData[1]
							thisMember = str(message.author.id)
							highScore = countData[3]
							print(f"lastNum = {lastNum}")
							print(f"nextNum = {nextNum}")
							print(f"lastMember = {lastMember}")
							print(f"thisMember = {thisMember}")
							print(f"highScore = {highScore}")
							if lastNum == output - 1 and lastMember != thisMember: # success
								await message.add_reaction(EMOJI_CHECKMARK)
								UpdateCount("NUM", serverID, output, message.author.id, 1, NULL)
								if output > highScore:
									await message.add_reaction(EMOJI_STAR)
									UpdateCount("HS", serverID, output, message.author.id, 1, output)
									if output == highScore + 1:
										await channelFrom.send(f"You just beat the High Score of {highScore}!")

							else: # fail
								if lastNum != output - 1 and lastMember != thisMember: # wrong num
									await channelFrom.send(f"{message.author.mention} broke it with {output}!  The next number was {nextNum}.")
								elif lastNum == output - 1 and lastMember == thisMember: # same author
									await channelFrom.send(f"{message.author.mention} broke it at {lastNum}!  The same member can not count twice in a row.")
								elif lastNum != output - 1 and lastMember == thisMember: # wrong num, same author
									await channelFrom.send(f"{message.author.mention} broke it with {output}!  The same member can not count twice in a row, and the next number was {nextNum}.")
						
								await message.add_reaction(EMOJI_X)
								UpdateCount("STOP", serverID, 0, NULL, 0, NULL) # reset (but do not restart) the game
								await channelFrom.send(f"Count ended.  Use `{CMD_PREFIX}count start` to start a new one.")

						else:
							await channelFrom.send(f"There is not a count in progress to increment.  Use `{CMD_PREFIX}count start` to start one.")

			else: # not counting
				await channelFrom.send(f"{output}")

print("Count Botula is waking up...")
bot.start()
