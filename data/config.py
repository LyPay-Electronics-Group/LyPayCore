from os import getcwd as cwd, getenv
from dotenv import load_dotenv as load_dotenvy

load_dotenvy(".envy")


class PATHS:
    DATA = cwd() + '/data/'

    QR = DATA + 'QR/'

    STORES = DATA + 'stores/'
    USERS = DATA + 'users/'
    EMAIL = DATA + 'email/'

    STORES_ITEMS = STORES + 'items/'
    STORES_AVATARS = STORES + 'avatars/'

    USERS_AVATARS = USERS + 'avatars/'

    LAUNCH_SETTINGS = DATA + 'settings.json'

    all = (DATA, QR, STORES, EMAIL, STORES_ITEMS, STORES_AVATARS)


class CENSOR:
    CORRECT_NAME_LITERALS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя -–АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    CORRECT_LOGIN_LITERALS = set("0123456789abcdefghijklmnopqrstuvwxyz._-ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    STORE_NAME_LENGTH = 100
    STORE_DESCRIPTION_LENGTH = 900
    STORE_ITEM_NAME_LENGTH = 70


class IDGEN:
    TIMEOUT = .01

    USER_ID_LENGTH = 8
    STORE_ID_LENGTH = 3
    ITEM_ID_LENGTH = 7
    CHEQUE_ID_LENGTH = 6
    FPS_ID_LENGTH = 16

    USER_ID = "{year}{_}"
    STORE_ID = "{_}"
    ITEM_ID = "i{storeID}_{_}"
    CHEQUE_ID = "c{storeID}_{_}"
    FPS_ID = "{_}"


class EMAIL:
    class SUBJECTS:
        MAIN = "Регистрация в LyPay"
        GUEST = "Регистрация в LyPay: гостевой доступ"
        SHOPKEEPER = "LyPay: приглашение на Благотворительную Ярмарку-{year}"

    class PATHS:
        MAIN = PATHS.EMAIL + "main.html"
        GUEST = PATHS.EMAIL + "guest.html"
        STORE = PATHS.EMAIL + "store.html"
        USER_MANUAL = PATHS.EMAIL + "manual placeholder.pdf"
        STORE_MANUAL = PATHS.EMAIL + "manual placeholder.pdf"

    ACCESS_CODE_LENGTH = 24
    SENDER = "LyPay Electronics"


class TOKENIZER:
    CONFIG_REFRESH_DELTA = 10
    CONFIG_FILE = "tokens.json"

    PUBLIC_LIST = tuple(map(lambda t: t.strip(), getenv("LYPAY_PUBLIC_TOKENS").split(',')))
    ADMIN_LIST = tuple(map(lambda t: t.strip(), getenv("LYPAY_ADMIN_TOKENS").split(',')))


JWT_KEY = "crimsonmoonshinesuponatownthatissmearedinblood-criedthedivagivenintolament"
CHUNK_SIZE = 1024


VERSION = "v2.6c"
NAME = "Public API"
BUILD = 25
