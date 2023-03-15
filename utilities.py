from pathlib import Path
import json
import re
import discord
from roles import *
from datetime import datetime

monitor = {}

test_shops = []
test_orders = {}
games = ["minecraft", "roblox", "LOL", "CS:GO", "Valorant", "GOD", "Apex Legends", "Fortnite", "Overwatch", "GTA V", "Among Us", "Call of Duty", "Human", "Visual Studio", "Visual Studio Code", "Unity", "Pycharm", "Don't Starve", "IntelliJ", "Rider"]

def buy(guild : discord.Guild, user : discord.User, item_id : int):
    global test_orders

    file_name = guild.name.replace(' ', '_') + '.json';
    students = read(file_name)

    price = shop[item_id]["server_scores"][guild.id]

    if students[user.name]["score"] < price:
        return f"**{user.mention}** doesn't have enough points for **{shop[item_id]['title']}**"
    else:
        students[user.name]["score"] -= price
        write(file_name, students)

        #check if guild id in test orders
        if guild.id not in test_orders:
            test_orders[guild.id] = {
                user.name : [item_id]
            }
        #check if user name in guild id
        elif user.name not in test_orders[guild.id]:
            test_orders[guild.id][user.name] = [item_id]
        else:
            #check in shop already bought
            if item_id in test_orders[guild.id][user.name] and shop[item_id]["one_use"]:
                return f"**{user.mention}** already bought **{shop[item_id]['title']}**"

            test_orders[guild.id][user.name].append(item_id)
        return f"**{user.mention}** spent **{shop[item_id]['server_scores'][guild.id]}** points for **{shop[item_id]['title']}**"


def read(file_name: str):
    file_name = "save_logs\\" + file_name
    file = Path(file_name)

    if not file.is_file():
        return {}

    file = open(file_name)
    text = file.read()
    file.close();

    if text == '':
        return {}

    return json.loads(text)


def write(file_name: str, data: dict):
    if len(data) == 0: return

    file_name = "save_logs\\" + file_name
    file = Path(file_name)
    file.touch(exist_ok=True)

    file_stream = open(file_name, 'w')
    file_stream.write(json.dumps(data, indent=4))
    file_stream.close()


def get_role(score: int):
    role = ""

    for name, params in roles.items():
        if score >= params["score"]:
            role = name

    return role


async def add_points(file_name: str, score: int, accounts: discord.Member):
    students = read(file_name)

    for account in accounts:
        if account.name in students:
            students[account.name]["score"] += score

            if score >= 0:
                students[account.name]["total"] += score

            if account.nick != students[account.name]["nick"]:
                students[account.name]["nick"] = account.nick

        else:
            students[account.name] = {}
            students[account.name]["nick"] = account.nick
            students[account.name]["score"] = score

            if score > 0:
                students[account.name]["total"] = score
            else:
                students[account.name]["total"] = 0

            students[account.name]["entries"] = []

        students[account.name]["entries"].append(f"{score} | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    write(file_name, students)

    try:
        for account in accounts:
            # get role according to points
            role_name = get_role(students[account.name]["score"])
            # print(role_name)

            # if role is the same as the one the user has, skip
            if role_name == account.top_role.name:
                continue

            # get dall server roles
            account_roles = account.guild.roles

            # get role object by name
            role = None
            for r in account_roles:
                if r.name == role_name:
                    role = r
                    break

            # delete all user roles
            for r in account.roles:
                if r.name in roles:
                    await account.remove_roles(r)

            # add new role
            await account.add_roles(role)


    except Exception as e:
        print(e)


def get_code_language(code):
    js_words = {"let", "var", "in", ":"}
    cs_words = {"var", "class", "public", "private", ";", "{", "}"}
    py_words = {"def", "for", "in", ":"}

    code_words = re.findall(r"\w+", code)
    js_weight = sum(1 for word in code_words if word in js_words)
    cs_weight = sum(1 for word in code_words if word in cs_words)
    py_weight = sum(1 for word in code_words if word in py_words)

    if js_weight >= cs_weight and js_weight >= py_weight:
        return "js"
    elif cs_weight >= js_weight and cs_weight >= py_weight:
        return "cs"
    else:
        return "py"