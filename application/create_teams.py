import random
from typing import get_args
from itertools import chain
from functools import reduce

from application.types import Player, RolesType, TeamType


def create_teams(players: list[Player], team_size=5) -> tuple[list[dict[RolesType, Player | None]], set[Player]]:
    primary_roles: dict[RolesType, list[Player]] = {
        "top": [],
        "jungle": [],
        "mid": [],
        "adc": [],
        "support": []
    }

    secondary_roles: dict[RolesType, list[Player]] = {
        "top": [],
        "jungle": [],
        "mid": [],
        "adc": [],
        "support": []
    }

    # Organize players by their primary and secondary roles
    for player in players:
        primary_roles[player.primary_role].append(player)
        if player.secondary_role:
            secondary_roles[player.secondary_role].append(player)

    roles = get_args(RolesType)
    teams: list[TeamType]  = [{role: None for role in roles} for _ in range(len(players) // team_size)]

    for team in teams:
        for role in team.keys():
            if not primary_roles[role]:
                continue

            selected_player = random.choice(primary_roles[role])
            team[role] = selected_player

            # Remove the selected player from the pool
            primary_roles[role].remove(selected_player)  
            if selected_player.secondary_role:
                secondary_roles[selected_player.secondary_role].remove(selected_player)

    # TODO: teams are created not randomle. 
    #  First team will have all primary players, second will have only autofill and etc. 
    #  Need to fix that

    for team in teams:
        for role, player in team.items():
            # Role already taken, no need to select again
            if player:
                continue

            # Pool of players is empty, skip to next role
            if not secondary_roles[role]:
                continue

            selected_player = random.choice(secondary_roles[role])
            team[role] = selected_player

            # Remove the selected player from the pool
            secondary_roles[role].remove(selected_player)
            if selected_player in primary_roles[selected_player.primary_role]:
                primary_roles[selected_player.primary_role].remove(selected_player)

    leftover_players = set(chain(
        reduce(lambda x, y: x + y, primary_roles.values()),
        reduce(lambda x, y: x + y, secondary_roles.values())
    ))

    if not leftover_players:
        return teams, leftover_players

    for team in teams:
        for role, player in team.items():
            if player:
                continue

            if not leftover_players:
                return teams, leftover_players

            selected_player = random.choice(tuple(leftover_players))
            team[role] = selected_player
            leftover_players.remove(selected_player)  

    return teams, leftover_players


if __name__ == "__main__":
    # Sample list of players
    list_of_players: list[Player] = [
        Player(1, "url1", "top", "jungle"),
        Player(2, "url2", "mid", "jungle"),
        Player(3, "url3", "adc", "jungle"),
        Player(4, "url4", "jungle", "jungle"),
        Player(5, "url5", "support", "jungle"),
        Player(6, "url6", "top", "jungle"),
        Player(7, "url7", "top", "jungle"),
        Player(8, "url8", "top", "jungle"),
        Player(9, "url9", "top", "mid"),
        Player(10, "url10", "top", None),
        Player(11, "url11", "top", "adc"),
        Player(12, "url12", "top", "support"),
        Player(13, "url13", "top", "support"),
    ]

    # Create teams
    teams, leftover_players = create_teams(list_of_players)

    # Display teams
    for idx, team in enumerate(teams, start=1):
        print(f"Team {idx}:")
        for role, player in team.items():
            if player:
                print(f"  - {role.capitalize()}: {player.opgg_url} (Primary: {player.primary_role}, Secondary: {player.secondary_role})")
            else:
                print(f"  - {role.capitalize()}: Not filled")
        print()

    print("Not selected players: ")
    for index, player in enumerate(leftover_players):
        print(f"Player {index}: {player.opgg_url} (Primary: {player.primary_role}, Secondary: {player.secondary_role})")
