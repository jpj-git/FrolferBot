
import ast
import os
import random
import discord
import goog
import helpers
import pendulum

from dotenv import load_dotenv
from datetime import datetime
from keep_alive import keep_alive
from discord.ext import commands

load_dotenv()
keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='-')
votes = {}
event_details = ''
cal_event = discord.Embed()


@bot.command(name='vote',
             help=f'Adds your votes to the course(s) you list (case-insensitive). Ex: Wickham Veterans page\n'
                  f'If you include less than three, the first one in your list will be counted extra. '
                  f'Meaning, Wickham would be 3 votes for Wickham and Page Wickham would be 2 and 1, respectively. '
                  f'Additionally, enclose multi-word names in "". (Ex: vote for Maple Hill with "Maple Hill")'
             )
async def vote(ctx, vote1: str, vote2="", vote3=""):
    global votes

    username = ctx.message.author.name

    if votes and username in votes.keys():
        response = 'You\'ve already voted. Run "change_vote" to update it, if desired.'
    else:
        votes, response = helpers.vote(votes, username, vote1, vote2, vote3)

    await ctx.send(response)


@bot.command(name='admin_vote', help=f'Admin tool to add votes for specified player.')
@commands.has_role('Mastermind')
async def admin_vote(ctx, username, vote1: str, vote2="", vote3=""):
    global votes

    votes, response = helpers.vote(votes, username, vote1, vote2, vote3, True)

    await ctx.send(response)


@bot.command(name='admin_multivote', help=f'Admin tool to add votes for multiple players.')
@commands.has_role('Mastermind')
async def admin_multivote(ctx, multiple):
    global votes
    votes = ast.literal_eval(multiple)

    print('Overall votes:\n   ' + '\n   '.join(helpers.get_courses_from_votes(votes, True)))
    response = 'Admin voted on behalf of multiple users for:\n   ' + '\n   '.join(helpers.get_courses_from_votes(votes, True))

    await ctx.send(response)


@bot.command(name='change_vote',
             help=f'Update a vote(s) that has been cast (case-insensitive). Default: 1, max: 3.\n'
                  f'Example: if you voted for Wickham and want to update to Veterans it would be '
                  f'"Wickham Veterans" to change a single vote. If you voted Wickham all three times '
                  f'and want to update 2 or 3 of them, add those, respectively, to the end of the command. '
                  f'Additionally, enclose multi-word names in "". (Ex: update to/from Maple Hill with "Maple Hill")'
             )
async def change_vote(ctx, old_vote: str, new_vote: str, updates=1):
    global votes
    username = ctx.message.author.name

    votes, response = helpers.change_vote(votes, username, old_vote, new_vote, updates)

    await ctx.send(response)


@bot.command(name='admin_change', help=f'Admin tool to change votes for specified player.')
@commands.has_role('Mastermind')
async def admin_change(ctx, username, old_vote: str, new_vote: str, updates=1):
    global votes

    votes, response = helpers.change_vote(votes, username, old_vote, new_vote, updates, True)

    await ctx.send(response)


@bot.command(name='current_votes', help='Shows list of current votes.')
async def current_votes(ctx, by_person=False):
    if votes:
        response = 'Current votes:\n   ' + '\n   '.join(helpers.get_courses_from_votes(votes, by_person))
    else:
        response = 'No one has voted yet! Run "vote" to cast yours.'

    await ctx.send(response)


@bot.command(name='next_event', help='Picks a random course based on votes.')
async def next_event(ctx):
    response = event_details if event_details else pick_course(ctx)

    await ctx.send(response)
    if cal_event.description:
        await ctx.send(embed=cal_event)


def pick_course(ctx):
    global event_details

    if votes:
        course_pick = random.choice(helpers.get_courses_from_votes(votes))
        sunday = pendulum.now().next(pendulum.SUNDAY)
        cal_url = goog.create_calendar_event(course_pick, sunday.strftime('%Y%m%d'))
        # cal_url = goog.create_cal_event(course_pick, sunday)
        sunday_fmt = sunday.strftime("%m/%d")
        event_details = f'Next event: playing {course_pick} on Sunday, {sunday_fmt}.'
        cal_event.description = f'[Add Sunday, {sunday_fmt} at {course_pick} to calendar]({cal_url})'
        response = f'{ctx.message.guild.default_role}\n{event_details}'
    else:
        response = 'Votes are needed to pick the event details. Run "vote" to cast yours.'

    return response


@bot.command(name='ctp', help='Picks a random hole from those provided for Closest to Pin.')
async def closest_pin(ctx, *args):
    hole_pick = random.choice(args)
    response = f'{ctx.message.guild.default_role}\nClosest to pin hole: {hole_pick}.'

    await ctx.send(response)


@bot.command(name='admin_remove', help=f'Admin tool to remove votes for specified player.')
@commands.has_role('Mastermind')
async def admin_remove(ctx, username):
    global votes

    del votes[username]
    response = f'Admin removal of votes for {username}.'

    await ctx.send(response)


@bot.command(name='clear', help='Used to clear votes and event info after the round has taken place.')
@commands.has_role('Mastermind')
async def clear(ctx, only_event_details=False):
    global votes
    global event_details
    global cal_event

    event_details = ''
    cal_event = discord.Embed()

    if only_event_details:
        response = 'Cleared event details. Run "next_event" when you\'re ready to pick again.'
    else:
        votes.clear()
        response = 'Cleared the votes and event details. Ready for the voting again next week.'

    await ctx.send(response)


@bot.event
async def on_command_error(ctx, error):
    now = datetime.now().replace(microsecond=0)

    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.CommandError):
        await ctx.send(f'{error}. Use *-help* to see available commands.')

    with open('err.log', 'a') as error_log_file:
        error_log_file.write(f'{now} --- Unhandled error: {error}\n')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_member_join(member):
    welcome_msg = (f'Hi {member.name}, welcome to our disc golf league\'s server!\n\n'
                   f'Please have a read of our #league-rules channel which outlines how we approach this informal '
                   f'league. This includes the frequency we intend to play, handicap details, as well as the '
                   f'monetary info, if you feel like putting some money on the line. Check out the other channels '
                   f'for more discussion locations!\n'
                   f'See you on the course!\n'
                   f'  - Our small DG crew'
                   )

    await member.create_dm()
    await member.dm_channel.send(welcome_msg)


bot.run(TOKEN)
