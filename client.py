from app import db


class Client(db.Model):
    __tablename__ = 'clients'
    __bind_key__ = 'clients'

    number = db.Column(db.String(), primary_key=True)
    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())
    street = db.Column(db.String())
    city = db.Column(db.String())
    country = db.Column(db.String())
    order = db.Column(db.String())
    date = db.Column(db.String())
    morning = db.Column(db.Boolean())
    afternoon = db.Column(db.Boolean())
    evening = db.Column(db.Boolean())
    served = db.Column(db.Boolean())

    def __init__(
            self,
            number,
            street=None,
            city=None,
            country=None,
            longitude=None,
            latitude=None,
            # order detail
            order=None,
            date=None,
            morning=True,
            afternoon=True,
            evening=True,
            served=False
    ):
        self.number = number
        self.longitude = longitude
        self.latitude = latitude
        self.street = street
        self.city = city
        self.country = country
        self.order = order
        self.date = date
        self.morning = morning
        self.afternoon = afternoon
        self.evening = evening
        self.served = served     # to know when they job is taken care of

    def __repr__(self):
        return '<number {}>'.format(self.number)

    def serialize(self):
        return {
            'number': self.number,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'street': self.street,
            'city': self.city,
            'country': self.country,
            'order': self.order,
            'date': self.date,
            'morning': self.morning,
            'afternoon': self.afternoon,
            'evening': self.evening,
            'served': self.served
        }
