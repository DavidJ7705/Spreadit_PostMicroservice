from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
    likes: Mapped[list["LikeDB"]] = relationship(
        "LikeDB",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["CommentDB"]] = relationship(
        "CommentDB",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    
class LikeDB(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer ,nullable=False)# when users table is linked change from post to that
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("post.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    post: Mapped["PostDB"] = relationship(
        "PostDB",
        back_populates="likes"
    )
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),)

class CommentDB(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer ,nullable=False)# when users table is linked change from post to that
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("post.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    post: Mapped["PostDB"] = relationship(
         "PostDB",
         back_populates="comments"
    )

    