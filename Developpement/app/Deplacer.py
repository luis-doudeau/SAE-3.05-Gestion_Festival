from sqlalchemy import Column , Integer, TEXT, DATETIME
from sqlalchemy . ext . declarative import declarative_base

Base = declarative_base()

class Deplacer(Base):
    __tablename__ = "DEPLACER"
    idP = Column(Integer, primary_key = True)
    idTransport = Column(Integer, primary_key = True)
    lieuDepart = Column(TEXT, primary_key = True)
    lieuArrive = Column(TEXT,  primary_key = True)
    dateArrive = Column(DATETIME, primary_key = True)
    dateDepart = Column(DATETIME, primary_key = True)


    def __init__(self, idP, idTransport, lieuDepart, lieuArrive, dateArrive, dateDepart) -> None:
        self.idP = idP
        self.idTransport = idTransport
        self.lieuDepart = lieuDepart
        self.lieuArrive = lieuArrive
        self.dateArrive = dateArrive
        self.dateDepart = dateDepart

    def __repr__(self) -> str:
        return "ID Intervenant : " + str(self.idP) + " - ID Transport : " + str(self.idTransport)+ " - Lieu Depart : " + self.lieuDepart + " - Lieu Arrive : " + self.lieuArrive
        