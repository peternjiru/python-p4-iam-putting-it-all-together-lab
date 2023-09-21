#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        # json = request.get_json()
        # user = User(
        #     username=json['username'],
        #     image_url=json['image_url'],
        #     bio=json['bio'],

        # )
        # user.password_hash = json['password']  # Use the setter method
        # db.session.add(user)
        # db.session.commit()
        # session['user_id'] = user.id
        # return user.to_dict(), 201

        json = request.get_json()
        username = json.get('username')

        if username is None or username.strip() == "":
            return {'error': 'Invalid username'}, 422

        user = User(
            username=json['username'],
            image_url=json['image_url'],
            bio=json['bio'],

        )

        user.password_hash = json['password']  # Use the setter method
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id

        # return user.to_dict(), 201 # this returns the whole object -  not needed in the use case

        return (
            {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }
        ), 201


class CheckSession(Resource):
    def get(self):

        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return {'id': user.id, 'username': user.username, 'image_url': user.image_url, 'bio': user.bio}, 200

        return {}, 401


class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()

        if user:

            password = request.get_json()['password']

            if user and user.authenticate(password):
                session['user_id'] = user.id
                return {'id': user.id, 'username': user.username, 'image_url': user.image_url, 'bio': user.bio}, 200

            return {'error': 'Invalid username or password'}, 401

        return {'error': 'Invalid username or password'}, 401


class Logout(Resource):
    def delete(self):

        user_id = session.get('user_id')

        if user_id:
            session['user_id'] = None
            # return make_response(jsonify({}), 204) # if using make_response and jsonify - same result
            return {}, 204
        # added this here because the pytest code was not cleatring the user_id
        session['user_id'] = None
        return {'error': 'Unauthorized'}, 401


class RecipeIndex(Resource):

    def get(self):

        user_id = session.get('user_id')

        if user_id:
            recipes = Recipe.query.all()

            serialized_recipes = []
            for recipe in recipes:
                serialized_recipes.append(recipe.to_dict())

            return serialized_recipes, 200

        return {'error': 'Unauthorized'}, 401

    def post(self):
        json = request.get_json()

        if len(json['instructions']) <= 50:
            return {'error': 'Invalid Instructions'}, 422

        user_id = session.get('user_id')

        new_recipe = Recipe(
            title=json['title'],
            instructions=json['instructions'],
            minutes_to_complete=json['minutes_to_complete'],
            # also try session.get('user_id') or self.user_id later when done
            user_id=user_id,
        )

        db.session.add(new_recipe)
        db.session.commit()

        return new_recipe.to_dict(), 201


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
