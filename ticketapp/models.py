from ticketapp import db, app

# Models

class UserModel(db.Model):
    user_id = db.Column(db.Integer, primary_key=True) # will auto increment user_id from 1
    username = db.Column(db.String(32), nullable=False)


class TicketModel(db.Model):
    ticket_id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    issue = db.Column(db.String(200), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user_model.user_id'), nullable=False)
    raised_by = db.Column(db.Integer, db.ForeignKey('user_model.user_id'), nullable=False)

with app.app_context():
    db.create_all()