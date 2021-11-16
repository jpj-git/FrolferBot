# bot.py
import os
import random
import string
import pendulum
import discord
from dotenv import load_dotenv
from datetime import datetime
from keep_alive import keep_alive

from discord.ext import commands

load_dotenv()
keep_alive()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')
# votes = {}
votes = {
    'jaxper': ['Wickham', 'Wickham', 'Page'],
    'tester1': ['Veterans', 'Veterans', 'Veterans'],
    'tester2': ['Nichols', 'Cranbury', 'Salem']
}
event_details = ''


@bot.command(name='vote',
             help=f'Adds your votes to the course(s) you list (case-insensitive). Ex: Wickham Veterans page\n'
                  f'If you include less than three, the first one in your list will be counted extra. '
                  f'Meaning, Wickham would be 3 votes for Wickham and Page Wickham would be 2 and 1, respectively. '
                  f'Additionally, enclose multi-word names in "". (Ex: vote for Maple Hill with "Maple Hill"'
             )
async def vote(ctx, vote1: str, vote2="", vote3=""):
    username = ctx.message.author.name
    if votes and username in votes.keys():
        response = 'You\'ve already voted. Run "change_vote" to update it, if desired.'
    else:
        cleaned = clean_votes(vote1, vote2, vote3)
        votes.update({username: cleaned})

        print('Overall votes:\n   ' + '\n   '.join(get_courses_from_votes(True)))
        response = f'Voted for: {", ".join(cleaned)}'

    await ctx.send(response)

def clean_votes(vote1: str, vote2: str, vote3: str):
    if not vote2:
        vote2 = vote1
        vote3 = vote1
    elif not vote3:
        temp = vote2
        vote2 = vote1
        vote3 = temp

    return [string.capwords(vote1), string.capwords(vote2), string.capwords(vote3)]

@bot.command(name='change_vote',
             help=f'Update a vote(s) that has been cast (case-insensitive). Default: 1, max: 3.\n'
                  f'Example: if you voted for Wickham and want to update to Veterans it would be '
                  f'"Wickham Veterans" to change a single vote. If you voted Wickham all three times '
                  f'and want to update 2 or 3 of them, add those, respectively, to the end of the command. '
                  f'Additionally, enclose multi-word names in "". (Ex: update to/from Maple Hill with "Maple Hill"'
             )
async def change_vote(ctx, old_vote: str, new_vote: str, updates=1):
    global votes

    username = ctx.message.author.name
    courses_lower = [item.lower() for item in votes[username]]
    old_vote = string.capwords(old_vote)
    new_vote = string.capwords(new_vote)
    old_vote_count = list.count(votes[username], old_vote)

    if old_vote_count == 0:
        response = check_old_vote(old_vote, username)
    else:
        if updates > old_vote_count:
            updates = old_vote_count
        if updates > 3:
            updates = 3

        for x in range(updates):
            index = courses_lower.index(old_vote.lower())
            courses_lower[index] = new_vote

        votes[username] = [string.capwords(item) for item in courses_lower]
        print('Votes after update:\n   ' + '\n   '.join(get_courses_from_votes(True)))
        response = f'Updated {old_vote} to {new_vote}, {updates} time(s)'

    await ctx.send(response)

def check_old_vote(old_vote: str, user_voting: str):
    alt = ''
    options = []

    for course in votes[user_voting]:
        if old_vote.lower() in course.lower() and course not in options:
            options.append(course)
    if options:
        alt = f'Did you mean {", or ".join(sorted(options))}? '

    return f'{old_vote} isn\'t in your current list of votes. {alt}Run "current_votes" to verify list.'


@bot.command(name='current_votes', help='Shows list of current votes.')
async def current_votes(ctx, by_person=False):
    if votes:
        response = 'Current votes:\n   ' + '\n   '.join(get_courses_from_votes(by_person))
    else:
        response = 'No one has voted yet! Run "vote" to cast yours.'
    await ctx.send(response)

def get_courses_from_votes(by_person=False):
    votes_casted = []
    if not by_person:
        for val in votes.values():
            votes_casted.extend(val)
    else:
        for key in votes.keys():
            votes_casted.append(f'{key}: {votes[key]}')

    return sorted(votes_casted)

@bot.command(name='next_event', help='Picks a random course based on votes.')
async def next_event(ctx):
    response = event_details if event_details else pick_course()

    await ctx.send(response)


def pick_course():
    global event_details

    if votes:
        course_pick = random.choice(get_courses_from_votes())
        sunday = pendulum.now().next(pendulum.SUNDAY).strftime('%m/%d')
        event_details = f'Next event: playing {course_pick} on Sunday, {sunday}'
        response = event_details
    else:
        response = 'Votes are needed to pick the event details. Run "vote" to cast yours.'

    return response


@bot.command(name='clear', help='Used to clear votes and event info after the round has taken place.')
@commands.has_role('Mastermind')
async def clear(ctx, only_event_details=False):
    global votes
    global event_details

    if only_event_details:
        event_details = ''
        response = 'Cleared event details. Run "next_event" when you\'re ready to pick again.'
    else:
        votes.clear()
        event_details = ''
        response = 'Cleared the votes event details. Ready for the voting again next week.'

    await ctx.send(response)

@bot.event
async def on_command_error(ctx, error):
    now = datetime.now().replace(microsecond=0)

    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

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
