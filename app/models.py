from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey

class Base(DeclarativeBase):
    pass

class PostDB(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)# , unique=True). We will need to establish a foreign key relationship
    
    
