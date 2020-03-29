from app import db


class Volunteer(db.Model):
    __tablename__ = 'volunteers'

    number = db.Column(db.String(), primary_key=True)
    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())
    street_number = db.Column(db.Integer())
    street = db.Column(db.String())
    city = db.Column(db.String())
    country = db.Column(db.String())
    is_available_am = db.Column(db.Boolean())
    is_available_pm = db.Column(db.Boolean())

    def __init__(
            self,
            number,
            street_number=None,
            street=None,
            city=None,
            country=None,
            longitude=None,
            latitude=None,
            is_available_am=False,
            is_available_pm=False
    ):
        self.number = number
        self.longitude = longitude
        self.latitude = latitude
        self.street_number = street_number,
        self.street = street
        self.city = city
        self.country = country
        self.is_available_am = is_available_am
        self.is_available_pm = is_available_pm

    def __repr__(self):
        return '<number {}>'.format(self.number)

    def serialize(self):
        return {
            'number': self.number,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'street_number': self.street_number,
            'street': self.street,
            'city': self.city,
            'country': self.country,
            'is_available_am': self.is_available_am,
            'is_available_pm': self.is_available_pm
        }