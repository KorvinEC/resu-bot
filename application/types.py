from typing import Literal, Protocol, TypeAlias
from dataclasses import dataclass
from uuid import UUID, uuid4


RolesType: TypeAlias = Literal["top", "jungle", "mid", "adc", "support"]
PrimaryRoleType: TypeAlias = Literal["top", "jungle", "mid", "adc", "support", "fill"]
SecondaryRoleType: TypeAlias = PrimaryRoleType | None


class PlayerNoFillType(Protocol):
    primary_role: RolesType
    secondary_role: RolesType | None


@dataclass(frozen=True)
class Player:
    user_id: int
    opgg_url: str
    primary_role: PrimaryRoleType
    secondary_role: SecondaryRoleType
    uuid: UUID

    @staticmethod
    def create_and_validate(
        user_id: int,
        opgg_url: str,
        primary_role: PrimaryRoleType,
        secondary_role: SecondaryRoleType,
        uuid: UUID | None = None,
    ) -> "Player":
        if primary_role == secondary_role or primary_role == "fill":
            secondary_role = None
        if uuid is None:
            uuid = uuid4()
        return Player(user_id, opgg_url, primary_role, secondary_role, uuid)

    @property
    def discord_roles(self) -> str:
        return (
            f"[`{self.primary_role}`/`{self.secondary_role}`]"
            if self.secondary_role
            else f"[`{self.primary_role}`]"
        )

    @property
    def discord_mention(self) -> str:
        return f"<@{self.user_id}>"

    @property
    def discord_opgg_url(self) -> str:
        # return f"[op.gg]({self.opgg_url})"
        return f"{self.opgg_url}"

    def __str__(self):
        return f'Player({id(self)}, {self.user_id}, "{self.opgg_url}", <{self.primary_role}/{self.secondary_role}>)'

    def __repr__(self) -> str:
        return str(self)


TeamType = dict[RolesType, Player | None]
