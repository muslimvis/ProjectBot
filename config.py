from enum import Enum

token = '1629793126:AAHJk0wBcK5x9KBFlhzBs7bbTra1PTgeg3Q'
db_file = 'database.vdb'


class States(Enum):
    S_START = '1'
    S_ENTER_CAR = '2'
    S_ENTER_MODEL = '3'
    S_ENTER_GENERATION = '4'
    S_ENTER_YEAR = '5'
    S_ENTER_POWER = '6'
    S_ENTER_KM = '7'