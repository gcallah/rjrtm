from flask import Flask, jsonify, request
from flask_restx import Resource, Api, fields
from flask_cors import CORS
import data.states as ds
import data.cities as dc

app = Flask(__name__)
CORS(app)
api = Api(app)

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
MESSAGE = 'Message'
JOURNAL_EP = '/journal'
JOURNAL_RESP = 'journal'

# Models

state_model = api.model('State', {
    'code': fields.String(required=True, description='State code, e.g. NY'),
    'name': fields.String(required=True, description='State name, e.g. New York')
})

city_model = api.model('City', {
    'name': fields.String(required=True, description='City name'),
    'country': fields.String(required=True, description='Country where the city is located'),
    'population': fields.Integer(description='Population of the city')
})

journal_model = api.model('JournalEntry', {
    'entry': fields.String(required=True, description='Journal entry text')
})

# Endpoints

@api.route(HELLO_EP)
class HelloWorld(Resource):
    """Simple health check endpoint."""
    def get(self):
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """Return all available endpoints."""
    def get(self):
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route(JOURNAL_EP)
class Journal(Resource):
    """A simple journal endpoint."""
    def get(self):
        return {JOURNAL_RESP: 'RJRTM Journal'}


@api.route('/journal/add')
class JournalAdd(Resource):
    @api.expect(journal_model)
    def post(self):
        data = api.payload
        entry = data.get('entry')
        if not entry:
            return {'error': 'Entry is required'}, 400
        return {'message': 'Entry added', 'entry': entry}, 201

# State Endpoints
@api.route('/states')
class States(Resource):
    @api.marshal_list_with(state_model)
    def get(self):
        """Return all states from the database."""
        states = ds.read_all_states()
        return states

    @api.expect(state_model)
    def post(self):
        """Add a new state."""
        data = api.payload
        ds.create_state(data)
        return {'message': 'State added successfully', 'state': data}, 201

@api.route('/states/<string:code>')

class StateByCode(Resource):
    @api.marshal_with(state_model)
    def get(self, code):
        """Return a specific state by code."""
        state = ds.read_state_by_code(code)
        if state:
            return state, 200
        return {'error': 'State not found'}, 404

    @api.expect(state_model)
    def put(self, code):
        """Update a state by code."""
        data = api.payload
        updated = ds.update_state(code, data)
        if updated:
            return {'message': 'State updated', 'state': data}, 200
        return {'error': 'State not found'}, 404

    def delete(self, code):
        """Delete a state by code."""
        deleted = ds.delete_state(code)
        if deleted:
            return {'message': 'State deleted'}, 200
        return {'error': 'State not found'}, 404
    
# City Endpoints  
@api.route('/cities')
class Cities(Resource):
    @api.marshal_list_with(city_model)
    def get(self):
        """
        Return all cities, with optional filtering and pagination.

        Query Parameters:
        - country: filter cities by country name
        - limit: number of results to return (default 50)
        - offset: number of results to skip (default 0)
        """
        # Get query parameters from URL
        country = request.args.get("country")
        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)

        # Fetch all cities from the data layer
        cities = dc.get_all_cities()

        # Optional filter by country
        if country:
            cities = [c for c in cities if c.get("country") == country]

        # Apply pagination
        cities = cities[offset : offset + limit]

        return cities
    @api.expect(city_model)
    def post(self):
        """Add a new city."""
        data = api.payload
        if not data or "name" not in data:
            return {"error": "City name required"}, 400
        dc.add_city(data)
        return {'message': 'City added successfully', 'city': data}, 201

@api.route('/cities/<string:name>')
class CityByName(Resource):
    def get(self, name):
        """Return a specific city by name."""
        city = dc.get_city_by_name(name)
        if city:
            return city, 200
        return {'error': 'City not found'}, 404

    @api.expect(city_model)
    def put(self, name):
        """Update a city by name."""
        updates = api.payload
        if dc.update_city(name, updates):
            return {'message': 'City updated'}, 200
        return {'error': 'City not found'}, 404

    def delete(self, name):
        """Delete a city by name."""
        if dc.delete_city(name):
            return {'message': 'City deleted'}, 200
        return {'error': 'City not found'}, 404
