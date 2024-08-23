from sqlalchemy import Boolean, Column, ForeignKey,LargeBinary, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import base64

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)
    date = Column(String)
    image = Column(LargeBinary, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "quantity": self.quantity,
            "price": self.price,
            "date": self.date,
            "image": base64.b64encode(self.image).decode('utf-8') if self.image else None
        }