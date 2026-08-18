from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import INTEGER, SMALLINT, TEXT, VARCHAR, REAL, JSON, BOOLEAN, Index
from sqlalchemy.ext.asyncio import AsyncAttrs

from typing import Any


class Base(AsyncAttrs, DeclarativeBase):
    def to_tuple(self) -> tuple:
        return tuple(getattr(self, col) for col in self.__table__.c.keys())

    def to_list(self) -> list:
        return [getattr(self, col) for col in self.__table__.c.keys()]

    def to_dict(self) -> dict:
        return {col: getattr(self, col) for col in self.__table__.c.keys()}


# SCHEMA : Public

class __AccessCodesBase(Base):
    code:  Mapped[str] = mapped_column(TEXT, primary_key=True)
    email: Mapped[str] = mapped_column(TEXT)


class AccessCodesGuest(__AccessCodesBase):
    __tablename__ = "access_codes_guest"


class AccessCodesMain(__AccessCodesBase):
    __tablename__ = "access_codes_main"


class Lot(Base):
    __tablename__ = "auction"

    lotID:     Mapped[int]  = mapped_column(SMALLINT, primary_key=True)
    name:      Mapped[str]  = mapped_column(TEXT)
    price:     Mapped[int]  = mapped_column(INTEGER)
    auctionID: Mapped[int]  = mapped_column(SMALLINT)
    confirmed: Mapped[bool] = mapped_column(BOOLEAN,  default=False)


class Cheque(Base):
    __tablename__ = "cheques"

    chequeID: Mapped[str]            = mapped_column(TEXT,    primary_key=True)
    storeID:  Mapped[str]            = mapped_column(TEXT)
    unix:     Mapped[float]          = mapped_column(REAL)
    customer: Mapped[int]            = mapped_column(INTEGER)
    items:    Mapped[dict[str, Any]] = mapped_column(JSON)
    active:   Mapped[bool]           = mapped_column(BOOLEAN, default=True)


class CorporationEntry(Base):
    __tablename__ = "corporation"

    name:     Mapped[str] = mapped_column(TEXT)
    category: Mapped[str] = mapped_column(TEXT)
    email:    Mapped[str] = mapped_column(TEXT)


class FPS(Base):
    __tablename__ = "fps"

    ID:            Mapped[str]        = mapped_column(TEXT,    primary_key=True)
    author:        Mapped[str]        = mapped_column(TEXT)
    author_type:   Mapped[str]        = mapped_column(VARCHAR)
    description:   Mapped[str | None] = mapped_column(TEXT)
    amount:        Mapped[int]        = mapped_column(INTEGER)
    payed:         Mapped[int | None] = mapped_column(INTEGER)
    cheque:        Mapped[str | None] = mapped_column(TEXT)
    unix_creation: Mapped[float]      = mapped_column(REAL)
    unix_payment:  Mapped[float]      = mapped_column(REAL)


class HistoryEntry(Base):
    __tablename__ = "history"

    ID_out: Mapped[str]   = mapped_column(TEXT)
    ID_in:  Mapped[str]   = mapped_column(TEXT)
    value:  Mapped[int]   = mapped_column(INTEGER)
    unix:   Mapped[float] = mapped_column(REAL)


class Item(Base):
    __tablename__ = "items"

    itemID:  Mapped[str]  = mapped_column(TEXT,    primary_key=True)
    storeID: Mapped[str]  = mapped_column(TEXT)
    name:    Mapped[str]  = mapped_column(TEXT)
    price:   Mapped[int]  = mapped_column(INTEGER)
    active:  Mapped[bool] = mapped_column(BOOLEAN, default=True)


class Lottery(Base):
    __tablename__ = "lottery"

    ID:   Mapped[str]   = mapped_column(TEXT, primary_key=True)
    unix: Mapped[float] = mapped_column(REAL)


class Promo(Base):
    __tablename__ = "promo"

    ID:     Mapped[str]  = mapped_column(TEXT,    primary_key=True)
    value:  Mapped[int]  = mapped_column(INTEGER)
    author: Mapped[str]  = mapped_column(TEXT)
    active: Mapped[bool] = mapped_column(BOOLEAN, default=True)


class Shopkeeper(Base):
    __tablename__ = "shopkeepers"

    userID:  Mapped[int] = mapped_column(INTEGER, primary_key=True)
    storeID: Mapped[str] = mapped_column(TEXT,    primary_key=True)

    __table_args__ = (
        Index("idx_storeID", "storeID"),
    )


class StoreFormLink(__AccessCodesBase):
    __tablename__ = "store_form_link"


class Store(Base):
    __tablename__ = "stores"

    ID:          Mapped[str]        = mapped_column(TEXT,     primary_key=True)
    name:        Mapped[str]        = mapped_column(TEXT)
    hostID:      Mapped[int]        = mapped_column(INTEGER)
    description: Mapped[str]        = mapped_column(TEXT)
    avatar:      Mapped[bool]       = mapped_column(BOOLEAN,  default=False)
    balance:     Mapped[int]        = mapped_column(INTEGER,  default=0)
    hostEmail:   Mapped[str]        = mapped_column(TEXT)
    auctionID:   Mapped[int | None] = mapped_column(SMALLINT)
    placeID:     Mapped[str | None] = mapped_column(TEXT)


class User(Base):
    __tablename__ = "users"

    ID:          Mapped[int]        = mapped_column(INTEGER, primary_key=True)
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

class __FirewallBaseClass(Base):
    ID:      Mapped[str]        = mapped_column(TEXT,    primary_key=True)
    unix:    Mapped[float]      = mapped_column(REAL)
    access:  Mapped[bool]       = mapped_column(BOOLEAN)
    comment: Mapped[str | None] = mapped_column(TEXT)


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
    "Lot",
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
