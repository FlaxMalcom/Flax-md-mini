from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flax_ultra_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flax_ultra.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

client = OpenAI(api_key="https://api.giftedtech.web.id/api/ai/mistral?apikey=gifted_api_6kuv56877d&q=")

# ------------------ DATABASE ------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.Text)
    reply = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.create_all()

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return render_template_string(open("index.html").read())

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "registered"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        login_user(user)
        return jsonify({"status": "success"})
    return jsonify({"status": "failed"})

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json['message']

    if user_message.lower() in ["hi","hello","hey"]:
        reply = "Hi, I am Flax Malcom AI, how can I help you today 🙂"
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Flax Malcom AI ULTRA, futuristic and intelligent."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content

    # Save memory
    memory = Memory(user_id=current_user.id, message=user_message, reply=reply)
    db.session.add(memory)
    db.session.commit()

    return jsonify({"reply": reply})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
