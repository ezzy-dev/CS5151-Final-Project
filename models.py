from sqlalchemy import Column, Integer, String

from app import db

class Test(db.Model):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    def __str__(self):
        return self.name