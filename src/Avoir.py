from sqlalchemy import Column , Integer, Text
from sqlalchemy . ext . declarative import declarative_base

Base = declarative_base()

class Avoir(Base):
    __tablename__ = "AVOIR"
    idC = Column(Integer, primary_key = True)
    idregime = Column(Integer, primary_key = True)

    def __init__(self, idC, idregime) -> None:
        self.idC = idC
        self.idregime = idregime

    def __repr__(self) -> str:
        return "ID consommateur : " + str(self.idC) + ", ID regime : " + str(self.idregime)
