from flask import Flask
from flask_restful import reqparse, abort, Resource, Api, marshal_with, fields
from appointment import AppointmentStore


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('name')

doctor_fields = {
    'id': fields.Integer,
    'name': fields.String,
}

NEXT_ID = 0


class Doctor(Resource):
    def __init__(self, **kwargs):
        self.store = kwargs['store']

    def abort_if_doctor_doesnt_exist(self, id):
        if id not in self.store:
            abort(404, message="Doctor {} doesn't exist".format(id))

    @marshal_with(doctor_fields)
    def get(self, id):
        self.abort_if_doctor_doesnt_exist(id)
        return self.store[id]

    def delete(self, id):
        self.abort_if_doctor_doesnt_exist(id)
        del self.store[id]
        return '', 204


class DoctorList(Resource):
    def __init__(self, **kwargs):
        self.store = kwargs['store']

    def get(self):
        return [v for k, v in self.store.iteritems()]

    @marshal_with(doctor_fields)
    def post(self):
        global NEXT_ID
        args = parser.parse_args()
        doctor = {
            'id': NEXT_ID,
            'name': args['name'],
            'appointments': AppointmentStore()
        }
        self.store[NEXT_ID] = doctor
        NEXT_ID += 1
        return doctor, 201
