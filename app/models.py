from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint

class Base(DeclarativeBase):
    pass

class PostDB(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)# , unique=True). We will need to establish a foreign key relationship
    module_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
class LikeDB(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.user_id"),nullable=False)# when users table is linked change from post to that
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("post.id"), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),)

    