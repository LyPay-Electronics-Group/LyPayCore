from os import getcwd as cwd


class PATHS:
    DATA = cwd() + '/data/'

    QR = DATA + 'QR/'

    STORES = DATA + 'stores/'
    EMAIL = DATA + 'email/'

    STORES_ITEMS = STORES + 'items/'
    STORES_AVATARS = STORES + 'avatars/'

    LAUNCH_SETTINGS = DATA + 'settings.json'

    all = (DATA, QR, STORES, EMAIL, STORES_ITEMS, STORES_AVATARS)


VERSION = "test-1"
NAME = ""
BUILD = 6

NEW_LINE_ANCHOR = "[([*br*])]"
OPEN_CURLY_BRACKET_ANCHOR = "[([*ocb*])]"
CLOSE_CURLY_BRACKET_ANCHOR = "[([*ccb*])]"
QUOTATION_ANCHOR = "[([*q*])]"
SPACE_ANCHOR = "[([*s*])]"
