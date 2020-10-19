from flask import Flask,render_template,request,url_for,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

from sqlalchemy.orm import backref

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///db1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
migrate=Migrate(app,db)

class Todo(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    list_id = db.Column(db.Integer , db.ForeignKey('todo_list.id'),nullable=False)
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String, nullable=False)
    todos = db.relationship('Todo', backref='list')

@app.route('/')
def index():
    return redirect(url_for('view_list',list_id=1))

@app.route('/lists/<list_id>')
def view_list(list_id):
    return render_template('index.html',
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all(),
    lists=TodoList.query.order_by('id').all(),
    current_list=TodoList.query.filter_by(id=list_id).order_by('id').first())

@app.route('/lists/<list_id>/create', methods=['POST'])
def create_todo(list_id):
    error=False
    data={}
    try:
        desc=request.get_json()['description']
        item=Todo(description=desc,list_id=list_id)
        db.session.add(item)
        db.session.commit()
        data = jsonify({
            'description': item.description
        })
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if not error:
        return data

@app.route('/lists/create', methods=['POST'])
def create_list():
    error=False
    data={}
    try:
        n=request.get_json()['name']
        list=TodoList(name=n)
        db.session.add(list)
        db.session.commit()
        data = jsonify({
            'name': list.name,
            'id': list.id
        })
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    
    if not error:
        return data

@app.route('/todos/<todo_id>/completed', methods=['POST'])
def edit_checked(todo_id):
    error=False
    data={}
    try:
        comp=request.get_json()['completed']
        todo_id=todo_id.split('-')[1]
        item=Todo.query.get(todo_id)
        item.completed=comp
        db.session.commit()
        data = jsonify({
            'completed': item.completed
        })
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return data

@app.route('/todos/<todo_id>/delete', methods=['POST'])
def delete_item(todo_id):
    error=False
    data={}
    try:
        todo_id=todo_id.split('-')[1]
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
        data = jsonify({
            'deleted': True
        })
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return data

if __name__ == "__main__":
    app.run(port=5000, debug=True) #host='0.0.0.0' to make app available though the network