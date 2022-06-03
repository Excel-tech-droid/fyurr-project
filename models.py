#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(120))

  shows = db.relationship('Show', backref='venue', cascade='all, delete-orphan', lazy=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate(Done)

class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  genres = db.Column(db.ARRAY(db.String))
  website = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(120))

  shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate(Done)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def show_artist(self):
    # Returns a dictionary of artists for the show
    return {
        'artist_id': self.artist_id,
        'artist_name': self.artist.name,
        'artist_image_link': self.artist.image_link,
        # convert datetime to string
        'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }

  def show_venue(self):
    # Returns a dictionary of venues for the show
    return {
        'venue_id': self.venue_id,
        'venue_name': self.venue.name,
        'venue_image_link': self.venue.image_link,
        # convert datetime to string
        'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }