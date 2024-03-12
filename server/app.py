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

# default route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# all restaurants route
@app.route('/restaurants')
def restaurants():
    restaurants = db.session.query(Restaurant).all()

    if restaurants:
        return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200
    else:
        return jsonify({"Error":"No existing restaurants."}), 404

# fetching restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        return jsonify(restaurant.to_dict(include_pizzas=True)), 200
    else:
        return jsonify({"error":"Restaurant not found."}), 404
    
    
# deleting restaurant
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else: 
        return jsonify({"error": "Restaurant not found."}), 404


# fetching pizzas
@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas = Pizza.query.all()

    if pizzas:
        return jsonify([pizza.to_dict() for pizza in pizzas]), 200
    else:
        return jsonify({"Error":"Pizza not found"})


# create restaurant_pizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json
    price = data.get('price')
    restaurant_id = data.get('restaurant_id')
    pizza_id = data.get('pizza_id')

    if not all([price, restaurant_id, pizza_id]):
        return jsonify({"errors":["validation errors"]}), 400


    if not (1 <= price <= 30):
        return jsonify({"errors":["validation errors"]}), 400


    pizza = Pizza.query.filter_by(id=pizza_id).first()       
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()


    if not (pizza and restaurant):
        return jsonify({"errors": "Pizza or restaurant not found"}), 404        

    try:
        new_rp = RestaurantPizza(
            price = price,
            pizza_id = pizza_id,
            restaurant_id = restaurant_id
        )
        db.session.add(new_rp)
        db.session.commit()
        return jsonify(new_rp.to_dict()), 201
    except ValueError as e:
        return jsonify({"Error": [str(e)]}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)
