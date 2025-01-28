from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import rsa
from main import db, Base
import uuid

class Users(db.Model):
    __tablename__ = 'users'
    id = mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(unique=True, nullable = False)
    complete_password: Mapped[str] = mapped_column(nullable=False) # salt + hashed_pw received
    salt: Mapped[str] = mapped_column(nullable = False)
    email: Mapped[str] = mapped_column(unique = True,nullable = True)
    pub_key: Mapped[str] = mapped_column(nullable = True)

    # jwt: Mapped[str] = mapped_column(nullable=True) for future iterations maybe

    # not working rn dunno why TODO: check
    # def find_by_username(username):
    #     db.session.execute(db.select(Users).filter_by(username=username))
        


class Images(db.Model):
    __tablename__ = 'images'
    id: Mapped[int] = mapped_column(primary_key=True)
    image_hash: Mapped[str] = mapped_column(nullable = False)
    user_id = mapped_column(ForeignKey('users.id'), nullable=False)
    last_accessed: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # not working rn dunno why TODO: check
    def get_by_hash(image_hash):
        Images.query.filter_by(image_hash=image_hash).first_or_404()

class DevImages(db.Model):
    __tablename__ = 'dev_images'

    id: Mapped[int] = mapped_column(primary_key=True)
    filename : Mapped[str] = mapped_column(nullable=False)
    data : Mapped[bytes] = mapped_column(nullable=False)
    mimetype: Mapped[str] = mapped_column(nullable=False)

