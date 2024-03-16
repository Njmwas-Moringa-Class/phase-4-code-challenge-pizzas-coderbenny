#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

# default route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# all restaurants route
class Restaurants(Resource):

    def get(self):
        restaurants = db.session.query(Restaurant).all()

        if not restaurants:
            return jsonify({"Error":"No existing restaurants."}), 404
        return make_response(jsonify([restaurant.to_dict() for restaurant in restaurants]), 200)

api.add_resource(Restaurants, '/restaurants')    

# Restaurant by ID
class RestaurantByID(Resource):

    # Retrieving restaurant by ID
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        
        if not restaurant:
            return make_response(jsonify({"error":"Restaurant not found."}), 404)
        return make_response(jsonify(restaurant.to_dict(include_pizzas=True)), 200)

    # Deleting restaurant
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response(jsonify({"error":"Restaurant not found."}), 404)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


api.add_resource(RestaurantByID, '/restaurants/<int:id>')


# fetching pizzas
class Pizzas(Resource):

    def get(self):
        pizzas = Pizza.query.all()

        if not pizzas:
            return make_response(jsonify({"Error":"Pizza not found"}), 404)
        return make_response(jsonify([pizza.to_dict() for pizza in pizzas]), 200)


api.add_resource(Pizzas,'/pizzas')
    

# create restaurant_pizza
class AddRestaurantPizza(Resource):

    def post(self):
        data = request.json
        price = data.get('price')
        restaurant_id = data.get('restaurant_id')
        pizza_id = data.get('pizza_id')

        if not all([price, restaurant_id, pizza_id]):
            return make_response(jsonify({"errors":["validation errors"]}), 400)


        if not (1 <= price <= 30):
            return make_response(jsonify({"errors":["validation errors"]}), 400)


        pizza = Pizza.query.filter_by(id=pizza_id).first()       
        restaurant = Restaurant.query.filter_by(id=restaurant_id).first()


        if not (pizza and restaurant):
            return make_response(jsonify({"errors": "Pizza or restaurant not found"}), 404)        

        try:
            new_rp = RestaurantPizza(
                price = price,
                pizza_id = pizza_id,
                restaurant_id = restaurant_id
            )
            db.session.add(new_rp)
            db.session.commit()
            return make_response(jsonify(new_rp.to_dict()), 201)
        except ValueError as e:
            return make_response(jsonify({"Error": [str(e)]}), 500)

api.add_resource(AddRestaurantPizza, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
