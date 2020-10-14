from flask import Flask,render_template,request,url_for,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///db1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
migrate=Migrate(app,db)

class Todo(db.Model):
    __name__='todos'
    id = db.Column(db.Integer , primary_key=True)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


@app.route('/')
def index():
    return render_template('index.html',data=Todo.query.all())

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error=False
    data={}
    try:
        desc=request.get_json()['description']
        item=Todo(description=desc)
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

if __name__ == "__main__":
    app.run(port=5000, debug=True) #host='0.0.0.0' to make app available though the network