from os import getcwd as cwd


class PATHS:
    DATA = cwd() + '/data/'

    QR = DATA + 'QR/'

    IMAGES = DATA + 'images/'
    EMAIL = DATA + 'email/'

    STORES_KEYBOARDS = DATA + 'stores keyboards/'
    STORES_LOGOS = DATA + 'stores logos/'
    OLD_LOGOS = DATA + 'changed stores logos/'
    STORES_CHEQUES = DATA + 'cheques/'

    LAUNCH_SETTINGS = DATA + 'settings.json'

    all = (DATA, IMAGES, LAUNCH_SETTINGS, QR, STORES_KEYBOARDS, STORES_LOGOS, STORES_CHEQUES, OLD_LOGOS, EMAIL)


VERSION = "test-1"
NAME = ""
BUILD = 5

NEW_LINE_ANCHOR = "[([*br*])]"
OPEN_CURLY_BRACKET_ANCHOR = "[([*ocb*])]"
CLOSE_CURLY_BRACKET_ANCHOR = "[([*ccb*])]"
QUOTATION_ANCHOR = "[([*q*])]"
SPACE_ANCHOR = "[([*s*])]"
