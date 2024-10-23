import random
from typing import get_args, Iterable, Generator

from application.types import Player, RolesType, TeamType


def flatten[T](iterable: Iterable[T]) -> Generator[T, None, None]:
    for item in iterable:
        if isinstance(item, list):
            yield from flatten(item)  # Recursively yield items from sublists
        else:
            yield item


def create_teams(players: list[Player], team_size=5) -> tuple[list[dict[RolesType, Player | None]], set[Player]]:
    roles = get_args(RolesType)
    primary_roles: dict[RolesType, list[Player]] = {role: [] for role in roles}
    secondary_roles: dict[RolesType, list[Player]] = {role: [] for role in roles}
    autofill_players = []

    # Organize players by their primary and secondary roles
    for player in players:
        if player.primary_role == "fill":
            autofill_players.append(player)
            continue

        primary_roles[player.primary_role].append(player)

        if player.secondary_role is not None and player.secondary_role == "fill":
            autofill_players.append(player)
        elif player.secondary_role is not None:
            secondary_roles[player.secondary_role].append(player)

    teams: list[TeamType] = [{role: None for role in roles} for _ in range(len(players) // team_size)]

    # Primary roles

    for role in roles:
        random_players = random.sample(primary_roles[role], len(primary_roles[role]))
        random_teams = random.sample(teams, len(teams))

        for selected_player, team in zip(random_players, random_teams):
            team[role] = selected_player

            # Remove the selected player from the pool
            primary_roles[role].remove(selected_player)

            if selected_player.secondary_role is not None and selected_player.secondary_role == "fill":
                autofill_players.remove(selected_player)
            elif selected_player.secondary_role is not None:
                secondary_roles[selected_player.secondary_role].remove(selected_player)

    # Secondary roles

    for role in roles:
        random_players = random.sample(secondary_roles[role], len(secondary_roles[role]))
        filtered_teams = list(filter(lambda team: team[role] is None, teams))  # type: ignore
        random_teams = random.sample(filtered_teams, len(filtered_teams))

        for selected_player, team in zip(random_players, random_teams):
            print(role, selected_player, team)
            team[role] = selected_player

            # Remove the selected player from the pool
            secondary_roles[role].remove(selected_player)

            if selected_player.primary_role == "fill":
                continue

            if selected_player in primary_roles[selected_player.primary_role]:
                primary_roles[selected_player.primary_role].remove(selected_player)

    for team in teams:
        for role, player in team.items():
            if player is not None:
                continue

            if not autofill_players:
                break

            selected_player = random.choice(tuple(autofill_players))
            team[role] = selected_player
            autofill_players.remove(selected_player)

            if selected_player.secondary_role == "fill":
                secondary_roles[role].remove(selected_player)

    leftover_players = set(  # type: ignore
        (
            *flatten(primary_roles.values()),
            *flatten(secondary_roles.values()),
            *autofill_players,
        )
    )

    return teams, leftover_players


if __name__ == "__main__":
    # Sample list of players
    list_of_players: list[Player] = [
        Player.create_and_validate(1, "url1", "top", "jungle"),
        Player.create_and_validate(2, "url2", "mid", "jungle"),
        Player.create_and_validate(3, "url3", "adc", "jungle"),
        Player.create_and_validate(4, "url4", "jungle", "jungle"),
        Player.create_and_validate(5, "url5", "support", "jungle"),
        Player.create_and_validate(6, "url6", "top", "jungle"),
        Player.create_and_validate(7, "url7", "top", "jungle"),
        Player.create_and_validate(8, "url8", "top", "jungle"),
        Player.create_and_validate(9, "url9", "top", "jungle"),
        Player.create_and_validate(10, "url10", "top", None),
        Player.create_and_validate(11, "url11", "top", "jungle"),
        Player.create_and_validate(12, "url12", "top", "jungle"),
        Player.create_and_validate(13, "url13", "top", "jungle"),
    ]

    # Create teams
    teams, leftover_players = create_teams(list_of_players)

    # Display teams
    for idx, team in enumerate(teams, start=1):
        print(f"Team {idx}:")
        for role, player in team.items():
            if player:
                print(
                    f"  - {role.capitalize()}: id-{player.user_id} {player.opgg_url} (Primary: {player.primary_role}, Secondary: {player.secondary_role})"
                )
            else:
                print(f"  - {role.capitalize()}: Not filled")
        print()

    print("Not selected players: ")
    for index, player in enumerate(leftover_players):
        print(" - ", player)

    for team in teams:
        for role, player in team.items():
            if player is None:
                continue
            list_of_players.remove(player)

    print(list_of_players)
