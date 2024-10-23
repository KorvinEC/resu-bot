from pathlib import Path
import pickle

from application.types import Player


class DictDatabase:
    data: dict[int, list[Player]]
    DATABASE_FILENAME: str =  "discord_bot_database.pickle"

    def __init__(self, database_dict: dict[int, list[Player]]) -> None:
        self.data = database_dict

    def load_from_pickle(self):
        database_file = Path(self.DATABASE_FILENAME)
        if database_file.exists():
            with open(self.DATABASE_FILENAME, "rb") as read_file:
                self.data = pickle.load(read_file)

    def dump_pickle(self):
        with open(self.DATABASE_FILENAME, "wb") as write_file:
            pickle.dump(self.data, write_file)


DATABASE = DictDatabase({})
