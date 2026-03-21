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


class CENSOR:
    CORRECT_NAME_LITERALS = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя -–АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    CORRECT_LOGIN_LITERALS = set("0123456789abcdefghijklmnopqrstuvwxyz._-ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    STORE_NAME_LENGTH = 100
    STORE_DESCRIPTION_LENGTH = 900
    STORE_ITEM_NAME_LENGTH = 70


class IDGEN:
    TIMEOUT = .01

    USER_ID_LENGTH = 9
    STORE_ID_LENGTH = 3
    ITEM_ID_LENGTH = 7
    CHEQUE_ID_LENGTH = 6

    USER_ID = "{_}"
    STORE_ID = "{_}"
    ITEM_ID = "{storeID}_{_}"
    CHEQUE_ID = "{storeID}_{_}"


class EMAIL:
    class SUBJECTS:
        MAIN = "Регистрация в LyPay"
        GUEST = "Регистрация в LyPay: Гостевой доступ"
        SHOPKEEPER = "LyPay: приглашение на Благотворительную Ярмарку-2026"

    class PATHS:
        MAIN = PATHS.EMAIL + "main.html"
        GUEST = PATHS.EMAIL + "guest.html"
        STORE = PATHS.EMAIL + "store.html"
        USER_MANUAL = PATHS.EMAIL + "manual placeholder.pdf"
        STORE_MANUAL = PATHS.EMAIL + "manual placeholder.pdf"

    SENDER = "LyPay Electronics"


JWT_KEY = "crimsonmoonshinesuponatownthatissmearedinblood-criedthedivagivenintolament"
CHUNK_SIZE = 1024


VERSION = "v2.4c"
NAME = "API Release"
BUILD = 14
