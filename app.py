from flask import Flask, request, jsonify
from config import Config
from models import db, User
import psycopg2
from psycopg2 import sql
import click

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_database_if_not_exists():
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='1234', host='localhost')
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), ['mydatabase'])
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier('mydatabase')))
    
    cursor.close()
    conn.close()

@app.cli.command('initdb')
def initdb_command():
    """Create the database tables."""
    create_database_if_not_exists()
    with app.app_context():
        db.create_all()
    click.echo('Initialized the database.')

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(name=data['name'], phonenumber=data['phonenumber'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'phonenumber': user.phonenumber} for user in users])

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'name': user.name, 'phonenumber': user.phonenumber})

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.json
    user = User.query.get_or_404(id)
    user.name = data.get('name', user.name)
    user.phonenumber = data.get('phonenumber', user.phonenumber)
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name, 'phonenumber': user.phonenumber})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)