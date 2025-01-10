from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import rsa
from flask_sqlalchemy import SQLAlchemy
from main import Base
import uuid

class Users(Base):
    __tablename__ = 'users'
    id = mapped_column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    user_token: Mapped[str] = mapped_column(unique=True, nullable = False)
    email: Mapped[str] = mapped_column(unique = True,nullable = True)
    pub_key: Mapped[str] = mapped_column(nullable = False)

    def find_by_user_token(user_token):
        Users.query.filter_by(user_token=user_token).first_or_404()
        


class Images(Base):
    __tablename__ = 'images'
    id: Mapped[int] = mapped_column(primary_key=True)
    image_hash: Mapped[str] = mapped_column(nullable = False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    last_accessed: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_by_hash(image_hash):
        Images.query.filter_by(image_hash=image_hash).first_or_404()

