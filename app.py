from flask import Flask, jsonify, request
from flask_jwt import JWT, jwt_required
from flask_restful import Api, Resource, reqparse
from security import authenticate, identity
from resourcess.group import Group, GroupList
from resourcess.message import Message, MessageList
from resourcess.update import Update
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')

app = Flask(__name__)
app.secret_key = 'palash'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///surveyor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


JWT(app, authenticate, identity)

api.add_resource(Group, '/group/<string:chat_id>')
api.add_resource(GroupList, '/groups')
api.add_resource(Message, '/group/<string:chat_id>/message/<string:name>')
api.add_resource(MessageList, '/group/<string:chat_id>/messages')
api.add_resource(Update, '/{}'.format(TOKEN))

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
