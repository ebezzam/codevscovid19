from app import db


class Volunteer(db.Model):
    __tablename__ = 'volunteers'

    number = db.Column(db.String(), primary_key=True)
    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())
    street = db.Column(db.String())
    city = db.Column(db.String())
    country = db.Column(db.String())
    morning = db.Column(db.Boolean())
    afternoon = db.Column(db.Boolean())
    evening = db.Column(db.Boolean())
    available = db.Column(db.Boolean())

    def __init__(
            self,
            number,
            street=None,
            city=None,
            country=None,
            longitude=None,
            latitude=None,
            morning=False,
            afternoon=False,
            evening=False,
            available=True
    ):
        self.number = number
        self.longitude = longitude
        self.latitude = latitude
        self.street = street
        self.city = city
        self.country = country
        self.morning = morning
        self.afternoon = afternoon
        self.evening = evening
        self.available = available    # flag to know when free

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
            'morning': self.morning,
            'afternoon': self.afternoon,
            'evening': self.evening,
            'available': self.available
        }