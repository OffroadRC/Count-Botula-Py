# Count Botula

import os
import os.path
import mysql.connector
import ast
from asyncio.windows_events import NULL
import operator as op
import discord
from discord import app_commands
from discord.ext import commands
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

SD_CHANNEL_COUNTING = 977459615283417099
DATABASE_NAME = "RowBotTest"
SETTINGS_TABLE_PREFIX = "settings_"
CMD_PREFIX = '/'
EMOJI_CHECKMARK = '✅'
EMOJI_X = '❌'
EMOJI_STAR = '⭐'

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

print(f"Connecting to database '{DATABASE_NAME}'...")
RowBotTestDB = mysql.connector.connect(
	host=DBHOST,
	user=DBUSER,
	password=DBPASS,
	database=DBNAME
	)

print(f"Connected to {DATABASE_NAME}.")
DBcursor = RowBotTestDB.cursor()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=CMD_PREFIX, intents=intents)

@bot.event
async def on_ready():
	print(f"{inspect.currentframe().f_code.co_name}")
	synced = await bot.tree.sync()
	print(f"Synced {str(len(synced))} command(s).")

	print(f"Logged in to Discord as {bot.user}.")
	print("Guilds: ")
	for guild in bot.guilds:
		print(f"\n{guild.name}")
		tableName = SETTINGS_TABLE_PREFIX + str(guild.id)
		print(f"tableName: {tableName}")
		DBcursor.execute(f"CREATE TABLE IF NOT EXISTS {tableName} (Parameter VARCHAR(255), Value VARCHAR(255))")
		print(f"Created/Confirmed table '{tableName}'\n")

	channel = bot.get_channel(SD_CHANNEL_COUNTING)
	await channel.send(content="ONE count bot!  Ah, ah, ah!")


def PrintTable(table_name):
	DBcursor.execute(f"SELECT * FROM {table_name}")
	table_data = DBcursor.fetchall()
	print(f"fetchall:\n{table_data}")
	return table_data


def UpdateCount(operation, server_id, count, member, is_running, high_score):
	if operation == "NUM":
		DBcursor.execute(
			f"UPDATE counting" \
			f" SET LastNum='{count}', LastMember='{member}'" \
			f" WHERE ServerID='{server_id}'")
	elif operation == "HS":
		DBcursor.execute(
			f"UPDATE counting" \
			f" SET HighScore='{high_score}'" \
			f" WHERE ServerID='{server_id}'")
	elif operation == "START":
		DBcursor.execute(
			f"INSERT INTO counting (ServerID, LastNum, LastMember, IsRunning, HighScore)" \
			f" VALUES('{server_id}', '{count}', '{member}', '{is_running}', '{high_score}')" \
			f" ON DUPLICATE KEY UPDATE LastNum='{count}', LastMember='{member}', IsRunning='{is_running}'")
	elif operation == "PAUSE":
		DBcursor.execute(
			f"UPDATE counting SET IsRunning='{is_running}'" \
			f" WHERE ServerID='{server_id}'")
	elif operation == "STOP":
		DBcursor.execute(
			f"UPDATE counting" \
			f" SET LastNum='{count}', LastMember='{member}', IsRunning='{is_running}'" \
			f" WHERE ServerID='{server_id}'")
	elif operation == "RESTART":
		DBcursor.execute(
			f"UPDATE counting" \
			f" SET LastNum='{count}', LastMember='{member}', IsRunning='{is_running}'" \
			f" WHERE ServerID='{server_id}'")

	RowBotTestDB.commit()


def GetCountData(server_id):
	print(f"{inspect.currentframe().f_code.co_name}")
	DBcursor.execute(f"SELECT LastNum, LastMember, IsRunning, HighScore FROM counting WHERE ServerID='{server_id}'")
	table_data = DBcursor.fetchall()
	print(f"table_data = {table_data}")
	if table_data != []:
		print(f"table_data[0] = {table_data[0]}")
		row = table_data[0]
		return row
	else:
		return table_data


def PrintCountMessage(cmd, guildID):
	print(f"{inspect.currentframe().f_code.co_name}")
	if cmd == "START":
		msg = "Started a new count."
	elif cmd == "STARTElse":
		msg = f"There is already a count in progress.  Use `{CMD_PREFIX}count restart` to restart."

	elif cmd == "PAUSE":
		msg = "Counting is now paused."
	elif cmd == "PAUSEElse":
		msg = f"There is not a count in progress to pause.  Use `{CMD_PREFIX}count start` to start one."

	elif cmd == "STOP":
		msg = f"Counting has been stopped and reset.  Use `{CMD_PREFIX}count start` to start a new one."
	elif cmd == "STOPElse":
		msg = f"There is not a count in progress to stop.  Use `{CMD_PREFIX}count start` to start one."

	elif cmd == "RESTART":
		msg = "The count in progress has now been restarted."
	elif cmd == "RESTARTElse":
		msg = "There was no count in progress.  A count has now been started."

	elif cmd == "HELP":
		msg = "__**Welcome to ~~Castle Anthrax~~ *the Help screen*!**__\n\n"\
			  \
			  "*Commands*\n"\
			 f"Usage: `{CMD_PREFIX}count [command]`\n"\
			  "`start` ---- Starts a new count if one is not already in progress.\n"\
			  "`pause` ---- Pauses the count so that `=` can be used safely without affecting count progress.\n"\
			  "`stop` ----- Resets the count without automatically starting a new count.\n"\
			  "`restart` -- Resets the count and starts a new one.  Can also be used like `start`.\n"\
			  "`help` ----- You are here. (Default)\n\n"\
			  \
			  "Begin messages with `=` to enter an expression to solve.  Can also be used as a calculator outside of counting!\n"\
			  "Example: `= 3*3`\n"\
			  "*Supported operations:*\n"\
			  "`+` --- Addition -------- `0+9`\n"\
			  "`-` --- Subtraction ----- `10-1`\n"\
			  "`*` --- Multiplication -- `3*3`\n"\
			  "`/` --- Division -------- `27/3`\n"\
			  "`()` -- Parentheses ----- `(6-3)*3`\n"\
			  "`**` -- Exponent -------- `3**2`   Tip: Exponent of 0.5 gives square root: `81**0.5`\n"

	elif cmd == "DEBUG":
		PrintTable("counting")
		msg = "Data sent to console."

	elif cmd == "NORECORD":
		msg = f"No count record exists for this server yet!  Use `{CMD_PREFIX}count start` to start one."

	else:
		msg = f"Command '{cmd}' is not recognized.  Type `{CMD_PREFIX}count` or `{CMD_PREFIX}count help` for a list of valid commands."

	return msg


def Math(expression):
	print(f"{inspect.currentframe().f_code.co_name}")
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
	print(f"{inspect.currentframe().f_code.co_name}")
	return eval_(ast.parse(expr, mode='eval').body)


# Math
def eval_(node):
	print(f"{inspect.currentframe().f_code.co_name}")
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


@bot.tree.command(name="count", description="Counting!")
@app_commands.describe(command="What would you like to do?")
@app_commands.choices(command=[
	app_commands.Choice(name="start", value="START"),
	app_commands.Choice(name="stop", value="STOP"),
	app_commands.Choice(name="pause", value="PAUSE"),
	app_commands.Choice(name="restart", value="RESTART"),
	app_commands.Choice(name="help", value="HELP"),
	app_commands.Choice(name="debug", value="DEBUG")
	])
async def count(interaction: discord.Interaction, command: app_commands.Choice[str]):
	print(f"{inspect.currentframe().f_code.co_name}")
	print(f"command = {command}")
	cmd = command.value
	guildID = interaction.guild_id
	print(f"cmd = {cmd}")
	table_data = GetCountData(guildID)
	print(f"table_data = {table_data}")
	if table_data != []:
		isRunning = table_data[2]
		print(f"isRunning = {isRunning}")
		if cmd == "START":			
			if isRunning == 0:
				UpdateCount(cmd, guildID, 0, NULL, 1, 0)
			else:
				cmd = cmd + "Else"

		elif cmd == "PAUSE":
			if isRunning == 1:
				UpdateCount(cmd, guildID, 0, NULL, 0, NULL)
			else:
				cmd = cmd + "Else"

		elif cmd == "STOP":
			if isRunning == 1:
				UpdateCount(cmd, guildID, 0, NULL, 0, NULL)
			else:
				cmd = cmd + "Else"

		elif cmd == "RESTART":
			UpdateCount(cmd, guildID, 0, NULL, 1, NULL)
			if isRunning == 0:
				cmd = cmd + "Else"

		await interaction.response.send_message(PrintCountMessage(cmd, guildID))

	else:
		if cmd == "START":
			UpdateCount(cmd, guildID, 0, NULL, 1, NULL)
		elif cmd == "PAUSE" or cmd == "STOP" or cmd == "RESTART":
			cmd = "NORECORD"

		await interaction.response.send_message(PrintCountMessage(cmd))


async def ProcessEquals(message):
	messageContent = message.content
	strippedMessage = messageContent.strip("= ")
	code, output = Math(strippedMessage)
	channelFrom = message.channel
	guildID = channelFrom.guild.id
	countData = GetCountData(guildID)
	print(f"countData = {countData}")
	isRunning = countData[2]
	channelCounting = bot.get_channel(SD_CHANNEL_COUNTING)

	if strippedMessage == "debug": # Run debug requests
		PrintTable("counting")
		return
	
	if channelFrom != channelCounting: # Process command as a math request if not in Counting channel and then exit
		await channelFrom.send(f"{output}")
		return	
	
	if countData == []: # Exit if no data
		await channelFrom.send(f"No count record exists for this server yet!  Use `{CMD_PREFIX}count start` to start one.")
		return

	if code != 0: # Exit if error occured
		return

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
			UpdateCount("NUM", guildID, output, message.author.id, 1, NULL)
			if output > highScore:
				await message.add_reaction(EMOJI_STAR)
				UpdateCount("HS", guildID, output, message.author.id, 1, output)
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
			UpdateCount("STOP", guildID, 0, NULL, 0, NULL) # reset (but do not restart) the game
			await channelFrom.send(f"Count ended.  Use `{CMD_PREFIX}count start` to start a new one.")

	else:
		await channelFrom.send(f"There is not a count in progress to increment.  Use `{CMD_PREFIX}count start` to start one.")


@bot.event
async def on_message(message):
	print(f"Message '{message}' sent.")
	print(f"{inspect.currentframe().f_code.co_name}")
	print(f"message:\n{message.content}")
	print(f"user:\n{message.author} {message.author.id}")
	messageContent = message.content

	if message.author.bot: # Exit if bot message
		return
	
	if messageContent.startswith('='): # Detect '=' commands
		await ProcessEquals(message)
		return

	await bot.process_commands(message) # Check to see if the message is a(nother type of) command, since overriding default on_message(), and then exit


print("Count Botula is waking up...")
bot.run(TOKEN)