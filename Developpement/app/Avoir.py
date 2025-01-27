from sqlalchemy import Column , Integer, Text
from sqlalchemy . ext . declarative import declarative_base

Base = declarative_base()

class Avoir(Base):
    __tablename__ = "AVOIR"
    idP = Column(Integer, primary_key = True)
    idRegime = Column(Integer, primary_key = True)

    def __init__(self, idP, idRegime) -> None:
        self.idP = idP
        self.idRegime = idRegime

    def __repr__(self) -> str:
        return "ID consommateur : " + str(self.idP) + ", ID regime : " + str(self.idRegime)
