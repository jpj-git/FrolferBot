# py
import string


def vote(votes: dict, username: str, vote1: str, vote2: str, vote3: str, is_admin=False):
    cleaned = clean_votes(vote1, vote2, vote3)
    votes.update({username: cleaned})

    print('Overall votes:\n   ' + '\n   '.join(get_courses_from_votes(votes, True)))
    if is_admin:
        response = f'Admin voted on behalf of {username} for: {", ".join(cleaned)}'
    else:
        response = f'Voted for: {", ".join(cleaned)}'

    return votes, response


def clean_votes(vote1: str, vote2: str, vote3: str):
    if not vote2:
        vote2 = vote1
        vote3 = vote1
    elif not vote3:
        temp = vote2
        vote2 = vote1
        vote3 = temp

    return [clean_str(vote1), clean_str(vote2), clean_str(vote3)]


def clean_str(course_name: str):
    stripped = course_name.strip(',. ')

    return string.capwords(stripped)


def change_vote(votes: dict, username: str, old_vote: str, new_vote: str, updates: int, is_admin=False):
    courses_lower = [item.lower() for item in votes[username]]
    old_vote = clean_str(old_vote)
    new_vote = clean_str(new_vote)
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

        votes[username] = [clean_str(item) for item in courses_lower]
        print('Votes after update:\n   ' + '\n   '.join(get_courses_from_votes(votes, True)))
        if is_admin:
            response = f'Admin updated {old_vote} to {new_vote}, {updates} time(s) on behalf of {username}'
        else:
            response = f'Updated {old_vote} to {new_vote}, {updates} time(s)'

    return votes, response


def check_old_vote(votes: dict, old_vote: str, user_voting: str):
    alt = ''
    options = []

    for course in votes[user_voting]:
        if old_vote.lower() in course.lower() and course not in options:
            options.append(course)

    if options:
        alt = f'Did you mean {", or ".join(sorted(options))}? '

    return f'{old_vote} isn\'t in your current list of votes. {alt}Run "current_votes" to verify list.'


def get_courses_from_votes(votes: dict, by_person=False):
    votes_casted = []

    if not by_person:
        for val in votes.values():
            votes_casted.extend(val)
    else:
        for key in votes.keys():
            votes_casted.append(f'{key}: {votes[key]}')

    return sorted(votes_casted)
