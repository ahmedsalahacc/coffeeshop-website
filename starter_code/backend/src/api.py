import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['GET'])
def get_drinks():
    drinks_query = Drink.query.all()
    print(drinks_query)
    if drinks_query:
        drinks_shorts = [i.short() for i in drinks_query]
        return jsonify({
            'drinks': drinks_shorts,
            'success': True
        }),200
    abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks_query = Drink.query.all()
    if drinks_query:
        drinks_long = [i.long() for i in drinks_query]
        return jsonify({
            'success': True,
            'drinks': drinks_long
        })
    #abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    req = request.get_json()

    try:
        recipe = req['recipe']
        if isinstance(recipe, dict):
            recipe = [recipe]
        title = req['title']
        drink = Drink()
        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.insert()
        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        })
    except BaseException:
        abort(400)
            
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(payload,id):
    req = request.get_json()
    try:
        drink_to_modify = Drink.query.filter(Drink.id == id)[0]
        title = req.get('title')
        recipe = req.get('recipe')
        if title:
            drink_to_modify.title = title
        if recipe:
            drink_to_modify.recipe = recipe
        
        drink_to_modify.update()
        return jsonify({'success': True, 
        'drinks': [drink_to_modify.long()]
        }),200

    except BaseException:
        abort(400)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink_to_delete = Drink.query.filter(Drink.id == id)[0]
    try:
        if not drink_to_delete:
            abort(404)

        drink_to_delete.delete()

        return jsonify({'success': True, 'delete': id}), 200

    except BaseException:
        abort(400)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found_404(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_err(error):
    err_code = error.status_code
    return jsonify({
        "success": False,
        "message": error.error['description'],
        "error": err_code
    }), err_code

# 400 error handler
@app.errorhandler(400)
def bad_request_400(error):
    return jsonify({
        "success": False,
        "message": 'Bad Request',
        "error": 400
    }), 400

# unauthorized (401)
@app.errorhandler(401)
def unauthorized_401(error):
    return jsonify({
        "success": False,
        "message": 'Unathorized',
        "error": 401
    }), 401

if __name__ == '__main__':
    app.run(debug = True)
