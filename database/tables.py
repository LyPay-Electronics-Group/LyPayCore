from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import INTEGER, SMALLINT, TEXT, VARCHAR, REAL, JSON, BOOLEAN, Index
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    def as_tuple(self) -> tuple:
        return tuple(getattr(self, col) for col in self.__table__.c.keys())

    def as_list(self) -> list:
        return [getattr(self, col) for col in self.__table__.c.keys()]

    def as_dict(self) -> dict:
        return {col: getattr(self, col) for col in self.__mapper__.attrs.keys()}


# SCHEMA : Public

class AccessCodesGuest(Base):
    __tablename__ = "access_codes_guest"

    code:  Mapped[str] = mapped_column(TEXT, primary_key=True)
    email: Mapped[str] = mapped_column(TEXT, unique=True)


class AccessCodesMain(Base):
    __tablename__ = "access_codes_main"

    code:  Mapped[str] = mapped_column(TEXT, primary_key=True)
    email: Mapped[str] = mapped_column(TEXT, unique=True)


class Lot(Base):
    __tablename__ = "auction"

    lotID:     Mapped[int]  = mapped_column("lotid", SMALLINT, primary_key=True)
    name:      Mapped[str]  = mapped_column(TEXT)
    price:     Mapped[int]  = mapped_column(INTEGER)
    auctionID: Mapped[int]  = mapped_column("auctionid", SMALLINT)
    confirmed: Mapped[bool] = mapped_column(BOOLEAN,  default=False)


class Cheque(Base):
    __tablename__ = "cheques"

    chequeID: Mapped[str]            = mapped_column("chequeid", TEXT,    primary_key=True)
    storeID:  Mapped[str]            = mapped_column("storeid", TEXT)
    unix:     Mapped[float]          = mapped_column(REAL)
    customer: Mapped[int]            = mapped_column(INTEGER)
    items:    Mapped[dict[str, int]] = mapped_column(JSON)
    active:   Mapped[bool]           = mapped_column(BOOLEAN, default=True)


class CorporationEntry(Base):
    __tablename__ = "corporation"

    name:     Mapped[str] = mapped_column(TEXT)
    category: Mapped[str] = mapped_column(TEXT)
    email:    Mapped[str] = mapped_column(TEXT, primary_key=True)


class FPS(Base):
    __tablename__ = "fps"

    ID:            Mapped[str]          = mapped_column("id", TEXT,    primary_key=True)
    author:        Mapped[str]          = mapped_column(TEXT)
    author_type:   Mapped[str]          = mapped_column(VARCHAR)
    description:   Mapped[str | None]   = mapped_column(TEXT)
    amount:        Mapped[int]          = mapped_column(INTEGER)
    payed:         Mapped[int | None]   = mapped_column(INTEGER)
    cheque:        Mapped[str | None]   = mapped_column(TEXT)
    unix_creation: Mapped[float]        = mapped_column(REAL)
    unix_payment:  Mapped[float | None] = mapped_column(REAL)


class HistoryEntry(Base):
    __tablename__ = "history"

    ID_out:   Mapped[str]   = mapped_column("id_out", TEXT)
    ID_in:    Mapped[str]   = mapped_column("id_in", TEXT)
    value:    Mapped[int]   = mapped_column(INTEGER)
    unix:     Mapped[float] = mapped_column(REAL)
    trns_srl: Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)


class Item(Base):
    __tablename__ = "items"

    itemID:  Mapped[str]  = mapped_column("itemid", TEXT, primary_key=True)
    storeID: Mapped[str]  = mapped_column("storeID", TEXT)
    name:    Mapped[str]  = mapped_column(TEXT)
    price:   Mapped[int]  = mapped_column(INTEGER)
    active:  Mapped[bool] = mapped_column(BOOLEAN, default=True)


class LotteryTicket(Base):
    __tablename__ = "lottery"

    ID:   Mapped[str]   = mapped_column("id", TEXT, primary_key=True)
    unix: Mapped[float] = mapped_column(REAL)


class Promo(Base):
    __tablename__ = "promo"

    ID:     Mapped[str]  = mapped_column("id", TEXT, primary_key=True)
    value:  Mapped[int]  = mapped_column(INTEGER)
    author: Mapped[str]  = mapped_column(TEXT)
    active: Mapped[bool] = mapped_column(BOOLEAN, default=True)


class Shopkeeper(Base):
    __tablename__ = "shopkeepers"

    userID:  Mapped[int] = mapped_column("userid", INTEGER, primary_key=True)
    storeID: Mapped[str] = mapped_column("storeid", TEXT,   primary_key=True)

    __table_args__ = (
        Index("idx_storeid", "storeid"),
    )


class StoreFormLink(Base):
    __tablename__ = "store_form_link"

    code:  Mapped[str] = mapped_column(TEXT, primary_key=True)
    email: Mapped[str] = mapped_column(TEXT, unique=True)


class Store(Base):
    __tablename__ = "stores"

    ID:          Mapped[str]        = mapped_column("id", TEXT, primary_key=True)
    name:        Mapped[str]        = mapped_column(TEXT)
    hostID:      Mapped[int]        = mapped_column("hostid", INTEGER)
    description: Mapped[str]        = mapped_column(TEXT)
    avatar:      Mapped[bool]       = mapped_column(BOOLEAN,  default=False)
    balance:     Mapped[int]        = mapped_column(INTEGER,  default=0)
    hostEmail:   Mapped[str]        = mapped_column(TEXT)
    auctionID:   Mapped[int | None] = mapped_column("auctionid", SMALLINT)
    placeID:     Mapped[str | None] = mapped_column("placeid", TEXT)


class User(Base):
    __tablename__ = "users"

    ID:          Mapped[int]        = mapped_column("id", INTEGER, primary_key=True)
    name:        Mapped[str]        = mapped_column(TEXT)
    login:       Mapped[str]        = mapped_column(TEXT)
    password:    Mapped[str]        = mapped_column(TEXT)
    category:    Mapped[str | None] = mapped_column(TEXT)
    email:       Mapped[str]        = mapped_column(TEXT)
    tag:         Mapped[str | None] = mapped_column(TEXT)
    balance:     Mapped[int]        = mapped_column(INTEGER, default=0)
    owner:       Mapped[str]        = mapped_column(TEXT)
    last_online: Mapped[float]      = mapped_column(REAL)
    avatar:      Mapped[bool]       = mapped_column(BOOLEAN, default=False)


# SCHEMA : Firewall

class FirewallAdminsEntry(Base):
    __tablename__ = "admins"
    __table_args__ = {"schema": "firewall"}

    ID:      Mapped[str]        = mapped_column("id", TEXT, primary_key=True)
    unix:    Mapped[float]      = mapped_column(REAL)
    access:  Mapped[bool]       = mapped_column(BOOLEAN)
    comment: Mapped[str | None] = mapped_column(TEXT)


class FirewallHighEntry(Base):
    __tablename__ = "high"
    __table_args__ = {"schema": "firewall"}

    ID:      Mapped[str]        = mapped_column("id", TEXT, primary_key=True)
    unix:    Mapped[float]      = mapped_column(REAL)
    access:  Mapped[bool]       = mapped_column(BOOLEAN)
    comment: Mapped[str | None] = mapped_column(TEXT)


class FirewallMainEntry(Base):
    __tablename__ = "main"
    __table_args__ = {"schema": "firewall"}

    ID:      Mapped[str]        = mapped_column("id", TEXT, primary_key=True)
    unix:    Mapped[float]      = mapped_column(REAL)
    access:  Mapped[bool]       = mapped_column(BOOLEAN)
    comment: Mapped[str | None] = mapped_column(TEXT)


class FirewallStoresEntry(Base):
    __tablename__ = "stores"
    __table_args__ = {"schema": "firewall"}

    ID:      Mapped[str]        = mapped_column("id", TEXT, primary_key=True)
    unix:    Mapped[float]      = mapped_column(REAL)
    access:  Mapped[bool]       = mapped_column(BOOLEAN)
    comment: Mapped[str | None] = mapped_column(TEXT)


__all__ = (
    "AccessCodesMain",
    "AccessCodesGuest",
    "Lot",
    "Cheque",
    "CorporationEntry",
    "FPS",
    "HistoryEntry",
    "Item",
    "LotteryTicket",
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