from sqlalchemy import Column, Integer, String, Boolean

from app import db

class Households(db.Model):
    __tablename__ = '400_households'
    HSHD_NUM = Column(Integer, primary_key=True)
    L = Column(Boolean)
    AGE_RANGE = Column(String(5))
    MARITAL = Column(String(10))
    INCOME_RANGE = Column(String(10))
    HOMEOWNER = Column(String(10))
    HSHD_COMPOSITION = Column(String(25))
    HH_SIZE = Column(String(5))
    CHILDREN = Column(String(5))
    def __str__(self):
        return self.HSHD_NUM