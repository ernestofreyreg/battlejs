from sparkpost import SparkPost
import boto
import json
import base64
from cs.keys import SPARKPOST_API_KEY, AWS_ACCESS_KEY, AWS_SECRET_KEY


sp = SparkPost(SPARKPOST_API_KEY)

def send_wellcome_email(player):
    sp.transmission.send(
        recipients=[str(player.email)],
        template='wellcome',
        substitution_data={
            "name": player.name,
            "authtoken": player.authtoken
        }
    )

def send_award_email(player):
    sp.transmission.send(
        recipients=[str(player.email)],
        template='level-up',
        substitution_data={
            "name": player.name,
            "authtoken": player.authtoken,
            "userlevel": player.level,
            "badge": player.avatar_number()
        }
    )

def send_challenge_email(player1, player2, match):
    sp.transmission.send(
        recipients=[str(player1.email)],
        template='challenge',
        substitution_data={
            "player1": player1.name,
            "player1avatar": player1.avatar_number(),
            "player2": player2.name if player2 else "UNKNOWN",
            "player2avatar": player2.avatar_number() if player2 else "39",
            "authtoken": player1.authtoken,
            "category": match.battle.category.name,
            "description": match.battle.description,
            "time": match.battle.maxtime,
            "level": match.battle.level,
            "tests": match.battle.visibletests_html(),
            "battleno": match.id
        }
    )

def send_challenge_completion_email(player1, player2, match):
    sp.transmission.send(
        recipients=[str(player1.email)],
        template='battle-notification',
        substitution_data={
            "player1": player1.name,
            "player1avatar": player1.avatar_number(),
            "player2": player2.name if player2 else "UNKNOWN",
            "player2avatar": player2.avatar_number() if player2 else "39",
            "authtoken": player1.authtoken,
            "category": match.battle.category.name,
            "description": match.battle.description,
            "time": match.battle.maxtime,
            "level": match.battle.level,
            "tests": match.battle.visibletests_html(),
            "battleno": match.id
        }
    )

def send_win_email(match, player_no):
    sp.transmission.send(
        recipients=[str(match.player1.email if player_no == 1 else match.player2.email)],
        template='winner',
        substitution_data={
            "player1": match.player1.name if player_no == 1 else match.player2.name,
            "useravatar": match.player1.avatar_number() if player_no == 1 else match.player2.avatar_number(),
            "player2": match.player2.name if player_no == 1 else match.player1.name,
            "authtoken": match.player1.authtoken if player_no == 1 else match.player2.authtoken,
            "category": match.battle.category.name,
            "description": match.battle.description,
            "points": match.pointsawarded,
            "level": match.battle.level,
            "tests": match.battle.visibletests_html(),
            "battleno": match.id
        }
    )

def send_lose_email(match, player_no):
    sp.transmission.send(
        recipients=[str(match.player1.email if player_no == 1 else match.player2.email)],
        template='loser',
        substitution_data={
            "player1": match.player1.name if player_no == 1 else match.player2.name,
            "useravatar": match.player1.avatar_number() if player_no == 1 else match.player2.avatar_number(),
            "player2": match.player2.name if player_no == 1 else match.player1.name,
            "authtoken": match.player1.authtoken if player_no == 1 else match.player2.authtoken,
            "category": match.battle.category.name,
            "description": match.battle.description,
            "points": 0,
            "level": match.battle.level,
            "tests": match.battle.visibletests_html(),
            "battleno": match.id
        }
    )

def send_no_winner_email(match, player_no):
    sp.transmission.send(
        recipients=[str(match.player1.email if player_no == 1 else match.player2.email)],
        template='no-winner',
        substitution_data={
            "player1": match.player1.name if player_no == 1 else match.player2.name,
            "useravatar": match.player1.avatar_number() if player_no == 1 else match.player2.avatar_number(),
            "player2": match.player2.name if player_no == 1 else match.player1.name,
            "authtoken": match.player1.authtoken if player_no == 1 else match.player2.authtoken,
            "category": match.battle.category.name,
            "description": match.battle.description,
            "points": 0,
            "level": match.battle.level,
            "tests": match.battle.visibletests_html(),
            "battleno": match.id
        }
    )

def send_lambda_request(fn, tests, encounter_id, player):

    awslambda = boto.connect_awslambda(aws_access_key_id=AWS_ACCESS_KEY,
                                       aws_secret_access_key=AWS_SECRET_KEY)

    player_fn = fn

    battle_tests = tests

    battle_test_string = "[" + ",".join(battle_tests) + "]"

    data = {
        "fn": base64.b64encode(player_fn),
        "tests": base64.b64encode(battle_test_string),
        "encounter_id": encounter_id,
        "player": player
    }

    awslambda.invoke_async("BattleJSTesting", json.dumps(data))


