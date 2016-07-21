from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class Manga(Base):
    __tablename__ = 'manga'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    key = Column(String(100), nullable=False)
    author = Column(String(100), nullable=True)
    artist = Column(String(100), nullable=True)
    year_of_release = Column(String(5), nullable=True)
    genres = Column(String(38), nullable=True, default='0' * 37)
    ongoing = Column(Boolean, nullable=True)


class Chapter(Base):
    __tablename__ = 'chapters'
    id = Column(Integer, primary_key=True)
    manga_id = Column(Integer, ForeignKey('manga.id'), nullable=False)
    manga = relationship(Manga)
    name = Column(String(100), nullable=True)
    number = Column(Integer, nullable=False)
    stored = Column(Boolean, nullable=False, default=False)
    path = Column(String(200), nullable=True)
    latest = Column(Boolean, nullable=False, default=False)


if __name__ == '__main__':
    # Create database
    engine = create_engine('sqlite:///manga.db')
    Base.metadata.create_all(engine)
