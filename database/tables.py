from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import INTEGER, SMALLINT, TEXT, VARCHAR, REAL, JSON, BOOLEAN, Index
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


# SCHEMA : Public

class __AccessCodesBase(Base):
    code:  Mapped[str] = mapped_column(TEXT, primary_key=True)
    email: Mapped[str] = mapped_column(TEXT, nullable=False)


class AccessCodesGuest(__AccessCodesBase):
    __tablename__ = "access_codes_guest"


class AccessCodesMain(__AccessCodesBase):
    __tablename__ = "access_codes_main"


class AuctionEntry(Base):
    __tablename__ = "auction"

    lotID:     Mapped[int]  = mapped_column(SMALLINT, nullable=False)
    name:      Mapped[str]  = mapped_column(TEXT,     nullable=False)
    price:     Mapped[int]  = mapped_column(INTEGER,  nullable=False)
    auctionID: Mapped[int]  = mapped_column(SMALLINT, nullable=False)
    confirmed: Mapped[bool] = mapped_column(BOOLEAN,  nullable=False, default=False)


class Cheque(Base):
    __tablename__ = "cheques"

    chequeID: Mapped[str]            = mapped_column(TEXT,    primary_key=True)
    storeID:  Mapped[str]            = mapped_column(TEXT,    nullable=False)
    unix:     Mapped[float]          = mapped_column(REAL,    nullable=False)
    customer: Mapped[int]            = mapped_column(INTEGER, nullable=False)
    items:    Mapped[dict[str, ...]] = mapped_column(JSON,    nullable=False)
    active:   Mapped[bool]           = mapped_column(BOOLEAN, nullable=False, default=True)


class CorporationEntry(Base):
    __tablename__ = "corporation"

    name:     Mapped[str] = mapped_column(TEXT, nullable=False)
    category: Mapped[str] = mapped_column(TEXT, nullable=False)
    email:    Mapped[str] = mapped_column(TEXT, nullable=False)


class FPS(Base):
    __tablename__ = "fps"

    ID:            Mapped[str]   = mapped_column(TEXT,    primary_key=True)
    author:        Mapped[str]   = mapped_column(TEXT,    nullable=False)
    author_type:   Mapped[str]   = mapped_column(VARCHAR, nullable=False)
    description:   Mapped[str]   = mapped_column(TEXT)
    amount:        Mapped[int]   = mapped_column(INTEGER, nullable=False)
    payed:         Mapped[int]   = mapped_column(INTEGER)
    cheque:        Mapped[str]   = mapped_column(TEXT)
    unix_creation: Mapped[float] = mapped_column(REAL,    nullable=False)
    unix_payment:  Mapped[float] = mapped_column(REAL,    nullable=False)


class HistoryEntry(Base):
    __tablename__ = "history"

    ID_out: Mapped[str]   = mapped_column(TEXT,    nullable=False)
    ID_in:  Mapped[str]   = mapped_column(TEXT,    nullable=False)
    value:  Mapped[int]   = mapped_column(INTEGER, nullable=False)
    unix:   Mapped[float] = mapped_column(REAL,    nullable=False)


class Item(Base):
    __tablename__ = "items"

    itemID:  Mapped[str]  = mapped_column(TEXT,    primary_key=True)
    storeID: Mapped[str]  = mapped_column(TEXT,    nullable=False)
    name:    Mapped[str]  = mapped_column(TEXT,    nullable=False)
    price:   Mapped[int]  = mapped_column(INTEGER, nullable=False)
    active:  Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)


class Lottery(Base):
    __tablename__ = "lottery"

    ID:   Mapped[str]   = mapped_column(TEXT, primary_key=True)
    unix: Mapped[float] = mapped_column(REAL, nullable=False)


class Promo(Base):
    __tablename__ = "promo"

    ID:     Mapped[str]  = mapped_column(TEXT,    primary_key=True)
    value:  Mapped[int]  = mapped_column(INTEGER, nullable=False)
    author: Mapped[str]  = mapped_column(TEXT,    nullable=False)
    active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)


class Shopkeeper(Base):
    __tablename__ = "shopkeepers"

    userid:  Mapped[int] = mapped_column(INTEGER, primary_key=True)
    storeid: Mapped[str] = mapped_column(TEXT,    primary_key=True)

    __table_args__ = (
        Index("idx_storeid", "storeid"),
    )


class StoreFormLink(__AccessCodesBase):
    __tablename__ = "store_form_link"


class Store(Base):
    __tablename__ = "stores"

    ID:          Mapped[str]  = mapped_column(TEXT,     primary_key=True)
    name:        Mapped[str]  = mapped_column(TEXT,     nullable=False)
    hostID:      Mapped[int]  = mapped_column(INTEGER,  nullable=False)
    description: Mapped[str]  = mapped_column(TEXT,     nullable=False)
    avatar:      Mapped[bool] = mapped_column(BOOLEAN,  nullable=False, default=False)
    balance:     Mapped[int]  = mapped_column(INTEGER,  nullable=False, default=0)
    hostEmail:   Mapped[str]  = mapped_column(TEXT,     nullable=False)
    auctionID:   Mapped[int]  = mapped_column(SMALLINT, nullable=False)
    placeID:     Mapped[str]  = mapped_column(TEXT)


class User(Base):
    __tablename__ = "users"

    ID:          Mapped[int]   = mapped_column(INTEGER, primary_key=True)
    name:        Mapped[str]   = mapped_column(TEXT,    nullable=False)
    login:       Mapped[str]   = mapped_column(TEXT,    nullable=False)
    password:    Mapped[str]   = mapped_column(TEXT,    nullable=False)
    category:    Mapped[str]   = mapped_column(TEXT)
    email:       Mapped[str]   = mapped_column(TEXT,    nullable=False)
    tag:         Mapped[str]   = mapped_column(TEXT)
    balance:     Mapped[int]   = mapped_column(INTEGER, nullable=False, default=0)
    owner:       Mapped[str]   = mapped_column(TEXT,    nullable=False)
    last_online: Mapped[float] = mapped_column(REAL,    nullable=False)
    avatar:      Mapped[bool]  = mapped_column(BOOLEAN, nullable=False, default=False)


# SCHEMA : Firewall

class __FirewallBaseClass(Base):
    ID:      Mapped[str]   = mapped_column(TEXT,    primary_key=True)
    unix:    Mapped[float] = mapped_column(REAL,    nullable=False)
    access:  Mapped[bool]  = mapped_column(BOOLEAN, nullable=False)
    comment: Mapped[str]   = mapped_column(TEXT)


class FirewallAdminsEntry(__FirewallBaseClass):
    __tablename__ = "firewall.admins"


class FirewallHighEntry(__FirewallBaseClass):
    __tablename__ = "firewall.high"


class FirewallMainEntry(__FirewallBaseClass):
    __tablename__ = "firewall.main"


class FirewallStoresEntry(__FirewallBaseClass):
    __tablename__ = "firewall.stores"


__all__ = (
    "AccessCodesMain",
    "AccessCodesGuest",
    "AuctionEntry",
    "Cheque",
    "CorporationEntry",
    "FPS",
    "HistoryEntry",
    "Item",
    "Lottery",
    "Promo",
    "Shopkeeper",
    "StoreFormLink",
    "Store",
    "User",
    "FirewallAdminsEntry",
    "FirewallHighEntry",
    "FirewallMainEntry",
    "FirewallStoresEntry",
)
