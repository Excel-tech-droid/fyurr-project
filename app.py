#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import sys
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)

# TODO: connect to a local postgresql database (DONE)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.order_by(Venue.state, Venue.city).all()
  data = []
  prev_city = None
  prev_state = None
  for venue in venues:
    venue_data = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(list(filter(lambda d: d.start_time > datetime.today(),
      venue.shows)))
    }
    if venue.city == prev_city and venue.state == prev_state:
      temp['venues'].append(venue_data)
    else:
      temp = {}
      temp['city'] = venue.city
      temp['state'] = venue.state
      temp['venues'] = [venue_data]
      data.append(temp)
    prev_city = venue.city
    prev_state = venue.state

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(
    Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for venue in venues:
    temp = {}
    temp['id'] = venue.id
    temp['name'] = venue.name
    temp['num_upcoming_shows'] = len(venue.shows)
    data.append(temp)
  
  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False

  try:
    venue = Venue.query.get(venue_id)
    past_shows = list(filter(lambda d: d.start_time < datetime. today(), venue.shows))

    upcoming_shows = list(filter(lambda d: d.start_time >= datetime.today(), venue.shows))

    past_shows = list(map(lambda d: d.show_artist(), past_shows))
    upcoming_shows = list(map(lambda d: d.show_artist(),  upcoming_shows))
  
    data = venue.__dict__
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
  except:
    error = True
  finally:
    if error:
      flash('An error occurred. Venue  could not be found.')
      return redirect(url_for('index'))
    else:
      return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm()
  error = False
  try:
    # TODO: modify data to be the data object returned from db insertion
    venue = Venue(name = form.name.data, state = form.state.data, city = form.city.data, address = form.address.data, genres = form.genres.data, phone = form.phone.data, website = form.website_link.data, image_link = form.image_link.data, facebook_link = form.facebook_link.data, seeking_talent = form.seeking_talent.data, seeking_description = form.seeking_description.data)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
    # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
     # on successful db insert, flash success
      flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + ' could not be deleted.')
    else:
      # on successful db insert, flash success
      flash('Venue ' + ' was successfully deleted!')
      return redirect(url_for('index'))

  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by(Artist.id).all()
  data = []
  for artist in artists:
    artist_data = {
      'id': artist.id,
      'name': artist.name
    }
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  response = {}
  response['count'] = len(search_results)
  response['data'] = search_results

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  error = False
  try:
    artist = Artist.query.get(artist_id)
    past_shows = list(filter(lambda d: d.start_time < datetime.today(), artist.shows))
    upcoming_shows = list(filter(lambda d: d.start_time >=  datetime.today(), artist.shows))
    past_shows = list(map(lambda d: d.show_venue(), past_shows))
    upcoming_shows = list(map(lambda d: d.show_venue(),   upcoming_shows))

    data = artist.__dict__
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
  except:
    error = True
  finally:
    if error:
      flash('An error occurred. Artist could not be found.')
      return redirect(url_for('index'))
    else:
      return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name 
  form.state.data = artist.state 
  form.city.data = artist.city
  form.genres.data = artist.genres 
  form.phone.data = artist.phone 
  form.website_link.data = artist.website 
  form.image_link.data = artist.image_link 
  form.facebook_link.data = artist.facebook_link 
  form.seeking_venue.data = artist.seeking_venue 
  form.seeking_description.data = artist.seeking_description 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  form = ArtistForm()
  error = False
  artist = Artist.query.get(artist_id)

  try:
    artist.name = form.name.data
    artist.state = form.state.data
    artist.city = form.city.data
    artist.genres = form.genres.data
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name 
  form.state.data = venue.state 
  form.city.data = venue.city 
  form.address.data = venue.address 
  form.genres.data = venue.genres 
  form.phone.data = venue.phone 
  form.website_link.data = venue.website 
  form.image_link.data = venue.image_link 
  form.facebook_link.data = venue.facebook_link 
  form.seeking_talent.data = venue.seeking_talent 
  form.seeking_description.data = venue.seeking_description 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing  
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = form.name.data
    venue.state = form.state.data
    venue.city = form.city.data
    venue.address = form.address.data
    venue.genres = form.genres.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  form = ArtistForm()
  error = False
  try:
      artist = Artist(name = form.name.data, state = form.state.data, city = form.city.data, genres = form.genres.data, phone = form.phone.data, website = form.website_link.data, image_link = form.image_link.data, facebook_link = form.facebook_link.data, seeking_venue = form.seeking_venue.data, seeking_description = form.seeking_description.data)
      db.session.add(artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if error:
          flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
      else:
          flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()

  data = []
  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.isoformat()
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  form = ShowForm()
  try:
      show = Show()
      show.artist_id = form.artist_id.data
      show.venue_id = form.venue_id.data
      show.start_time = form.start_time.data
      db.session.add(show)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
      if error:
          flash('An error occurred. Requested show could not be listed.')
      else:
          flash('Requested show was successfully listed')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
