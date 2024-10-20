from typing import Literal
from dataclasses import dataclass


RolesType = Literal["top", "jungle", "mid", "adc", "support"]


@dataclass(frozen=True)
class Player:
    user_id: int
    opgg_url: str
    primary_role: RolesType
    secondary_role: RolesType | None

    @staticmethod
    def create_and_validate(user_id: int, opgg_url: str, primary_role: RolesType, secondary_role: RolesType | None) -> "Player":
        if primary_role == secondary_role:
            secondary_role = None

        return Player(user_id, opgg_url, primary_role, secondary_role)


    @property
    def discord_roles(self) -> str:
        return f"[`{self.primary_role}`/`{self.secondary_role}`]" if self.secondary_role else f"[`{self.primary_role}`]"

    @property
    def discord_mention(self) -> str:
        return f"<@{self.user_id}>"
    
    @property
    def discord_opgg_url(self) -> str:
        return f"[op.gg]({self.opgg_url})"
    

TeamType = dict[RolesType, Player | None]

