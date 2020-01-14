#!/usr/bin/python3

from ff_espn_api import *

MAX_WINS = 13
 
def add_if_not_full(lineup, player):
    # do not add if player gained negative points
    if player.points < 0:
        return

    # player list for the current position (ex: WR)
    player_list = lineup.get(player.position)

    # max num of players is 1 per position, unless it's WR or RB
    max_size = 1
    if player.position == "WR" or player.position == "RB":
        # set max size to 2
        max_size = 2


    # if the player list is not full
    if len(player_list) < max_size:
        player_list.append(player)
        return
    else:
        # if the player is a flex, check if flex position is open
        if player.position == "WR" or player.position == "RB" or player.position == "TE":
            flex_list = lineup.get("FLEX")
            flex_max_size = 1
            # if flex is not full
            if len(flex_list) < flex_max_size:
                flex_list.append(player)

def get_ideal_lineup(score, is_home_lineup):
    if is_home_lineup:
        lineup = score.home_lineup
    else:
        lineup = score.away_lineup
    ideal_lineup = {
        "QB": [],   # size 1
        "RB": [],   # size 2
        "WR": [],   # size 2
        "TE": [],   # size 1
        "D/ST": [], # size 1
        "K" : [],   # size 1
        "FLEX" : [] # size 1
    }
    # Sort players in lineup by descending points
    for player in sorted(lineup, key=lambda player: player.points, reverse=True):
        add_if_not_full(ideal_lineup, player)
    
    return ideal_lineup

def initialize_team_records(league):
    team_records = dict()

    for team in league.teams:
        team_records[team.team_name] = team.wins

    return team_records

def initialize_team_points(league):
    team_points = dict()

    for team in league.teams:
        team_points[team.team_name] = {
            "PF" : 0.0,
            "PA" : 0.0
        }

    return team_points

league_id = ''
year = 2019
swid = ''
espn_s2 = ''

league = League(league_id, year, espn_s2, swid)

week = league.nfl_week

different_results = 0

team_records = initialize_team_records(league)

team_points = initialize_team_points(league)

# loop through each week
for curr_week in range(1, MAX_WINS):
    # load current week
    league.load_roster_week(curr_week)
    print("Week: " + str(curr_week))
    # print(team.roster)

    for score in league.box_scores(curr_week):
        # ------------------- HOME TEAM -------------------
        home_lineup = get_ideal_lineup(score, is_home_lineup=True)

        # Print ideal lineup score
        home_score = 0
        for list in home_lineup:
            for player in home_lineup.get(list):
                home_score += player.points


        # ------------------- AWAY TEAM -------------------
        away_lineup = get_ideal_lineup(score, is_home_lineup=False)

        # Print ideal lineup score
        away_score = 0
        for list in away_lineup:
            for player in away_lineup.get(list):
                away_score += player.points

        # Update PF and PA
        team_points[score.away_team.team_name]["PF"] += away_score
        team_points[score.away_team.team_name]["PA"] += home_score
        # Update PF and PA
        team_points[score.home_team.team_name]["PF"] += home_score
        team_points[score.home_team.team_name]["PA"] += away_score

        # If winner is different, mark the symbol
        home_symbol = ""
        away_symbol = ""
        if score.home_score > score.away_score:
            if home_score < away_score:
                away_symbol = " *W*"
                different_results += 1
                team_records[score.away_team.team_name] += 1
                team_records[score.home_team.team_name] -= 1

        if score.home_score < score.away_score:
            if home_score > away_score:
                home_symbol = " *W*"
                different_results += 1
                team_records[score.home_team.team_name] += 1
                team_records[score.away_team.team_name] -= 1


        if home_symbol != "" or away_symbol != "":
            print("Home Team: ", score.home_team.team_name, " : ", round(home_score, 2), home_symbol)
            print("Away Team: ", score.away_team.team_name, " : ", round(away_score, 2), away_symbol)

    print()

print("Games with different outcomes: ", different_results)

print("----What If?----\n")
for team in league.teams:
    print(team.team_name)
    print("Record before: ", team.wins, "-", team.losses)
    print("Record after : ", team_records[team.team_name], "-", MAX_WINS - team_records[team.team_name])

    print("PF before: ", round(team.points_for, 2), " - PA before: ", round(team.points_against, 2))
    print("PF after : ", round(team_points[team.team_name]["PF"], 2), " - PA after : ", round(team_points[team.team_name]["PA"], 2))
    print()