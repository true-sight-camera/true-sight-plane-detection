from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from main import db


class Users(db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    pub_key: Mapped[str]

    def find_by_username(username):
        Users.query.filter_by(username=username).first_or_404()
        


class Images(db.Model):
    __tablename__ = 'images'
    id: Mapped[int] = mapped_column(primary_key=True)
    image_hash: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey(Users.id))
    last_accessed: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_by_hash(image_hash):
        Images.query.filter_by(image_hash=image_hash).first_or_404()

