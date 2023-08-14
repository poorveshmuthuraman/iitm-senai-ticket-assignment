from flask_restful import Resource, reqparse, abort, fields, marshal_with
from ticketapp import db, api
from ticketapp.models import TicketModel, UserModel
import uuid

# CONSTANTS

## USER KEYS
USER_ID = "user_id"
USERNAME = "username"
TICKETS_RAISED = "tickets_raised"
TICKETS_ASSIGNED = "tickets_assigned"

## TICKET KEYS
TICKET_ID = "ticket_id"
ISSUE = "issue"
ASSIGNED_TO = "assigned_to"
RAISED_BY ="raised_by"

## POST/ticket RESPONSE 
MESSAGE = "message"
SUCCESS = "success"
DATA = "data"


#resource fields

ticket_post_data_resource_fields = {
   TICKET_ID: fields.String,
   ASSIGNED_TO: fields.Integer
}

ticket_post_resource_fields = {
    MESSAGE: fields.String,
    SUCCESS: fields.Boolean,
    DATA: fields.Nested(ticket_post_data_resource_fields)
}

ticket_resource_fields = {
    TICKET_ID: fields.String,
    ISSUE: fields.String,
    ASSIGNED_TO: fields.Integer,
    RAISED_BY: fields.Integer
}

user_resource_fields = {
    USER_ID: fields.Integer,
    USERNAME: fields.String,
}

# Resources

# User args
user_post_args = reqparse.RequestParser()
user_post_args.add_argument("username", type=str, help="username is required", required=True)
user_delete_args = reqparse.RequestParser()
user_delete_args.add_argument("user_id", type=int, help="user_id is required to delete user", required=True)

# Ticket args
ticket_post_args = reqparse.RequestParser()
ticket_post_args.add_argument("user_id", type=str, help="Ticket riser's user_id is required", required=True)
ticket_post_args.add_argument("issue", type=str, help="Description of the issue is required", required=True)
ticket_delete_args = reqparse.RequestParser()
ticket_delete_args.add_argument("ticket_id", type=str, help="ticket_id is required", required=True)


offset = -1
def get_assigned_user():
    global offset
    # Round Robin principle used to assign tickets
    # Quantum = 1 assignment per user
    # System moves to next user after one assignment
    
    users = UserModel.query.all()
    count = UserModel.query.count()
    offset += 1
    if count - 1 < offset:
        offset = 0

    return int(users[offset].user_id)

class Ticket(Resource):
    def get(self):
        tickets = TicketModel.query.all()
        ticket_dict = {}
        for ticket in tickets:
            ticket_dict[ticket.ticket_id] = {
                TICKET_ID: ticket.ticket_id,
                ISSUE: ticket.issue,
                ASSIGNED_TO: ticket.assigned_to,
                RAISED_BY: ticket.raised_by
            }

        return ticket_dict
    
    @marshal_with(ticket_post_resource_fields) 
    def post(self):
        args = ticket_post_args.parse_args()
        raised_by = args[USER_ID]
        user = UserModel.query.filter_by(user_id=raised_by).first()
        # check is user does not exist
        if not user:
            user_not_found_response = {
                MESSAGE: f"User {raised_by} does not exist, ticket cannot be raised",
                SUCCESS: False,
                DATA: {
                    TICKET_ID: None,
                    ASSIGNED_TO: None
                }
            }

            return user_not_found_response, 404
        
        issue = args[ISSUE]
        assigned_to = get_assigned_user() # need to do round robin
        ticket_id = str(uuid.uuid4())
        success_response = {
                MESSAGE: "Ticket raised successfully",
                SUCCESS: True,
                DATA: {
                    TICKET_ID: ticket_id,
                    ASSIGNED_TO: assigned_to,
                }
            }
        
        ticket = TicketModel(ticket_id=ticket_id, issue=issue, raised_by=raised_by, assigned_to=assigned_to)
        db.session.add(ticket)
        db.session.commit()
        return success_response, 200

    @marshal_with(ticket_resource_fields)
    def delete(self):
        args = ticket_delete_args.parse_args()
        ticket_id = args[TICKET_ID]
        ticket = TicketModel.query.filter_by(ticket_id=ticket_id).first()
        if not ticket:
            abort(404, message="Ticket with ticket_id = {} does not exist, cannot perform delete".format(ticket_id))
        db.session.delete(ticket)
        db.session.commit()

        return ticket, 202

class User(Resource):
    def get(self):
        users = UserModel.query.all()

        users_dict = {}
        for user in users:
            users_dict[user.user_id] = {
                USER_ID: user.user_id, 
                USERNAME: user.username
                }

        return users_dict
    
    @marshal_with(user_resource_fields)
    def post(self):
        args = user_post_args.parse_args()
        username = args[USERNAME]
        user = UserModel(username=username) # note user_id is auto-assigned during commit()
        db.session.add(user)
        db.session.commit()

        return user, 201
    
    @marshal_with(user_resource_fields)
    def delete(self):
        args = user_delete_args.parse_args()
        user_id = args[USER_ID]
        user = UserModel.query.filter_by(user_id=user_id).first()
        if not user:
            abort(404, message="User with user_id = {} does not exist, cannot perform delete".format(user_id))
        db.session.delete(user)
        db.session.commit()

        return user, 202

# routes
api.add_resource(Ticket, "/ticket")
api.add_resource(User, "/user")