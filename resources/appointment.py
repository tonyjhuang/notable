from flask import request
from flask_restful import reqparse, marshal_with, abort, Resource, fields
from datetime import datetime

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('patient', required=True)
parser.add_argument('time', required=True)
parser.add_argument('kind', choices=['New Patient', 'Follow-up'], required=True)


appointment_fields = {
    'id': fields.Integer,
    'patient': fields.String,
    'time': fields.DateTime,
    'kind': fields.String,
}

NEXT_ID = 0


def parse_date_str_or_abort(date_str, format):
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        abort(400, message="Invalid time string: {}. Expected: '{}'".format(date_str, format))


# Stores the appointments for a single doctor in memory in two separate data structures to
# speed up querying by id and by datetime
class AppointmentStore:
    def __init__(self):
        # {appt_id -> appt}
        self.id_store = {}
        # {datetime -> [appt_id]}
        self.datetime_store = {}

    def fetch_all(self):
        return [v for k, v in self.id_store.iteritems()]

    def fetch_by_id_or_abort(self, appt_id):
        if appt_id not in self.id_store:
            abort(404, message="Appointment {} doesn't exist".format(appt_id))
        return self.id_store[appt_id]

    def fetch_by_date(self, date):
        return filter(lambda a: a['time'].date() == date, self.fetch_all())

    def can_accommodate(self, time_str):
        return len(self.datetime_store.get(time_str, [])) < 3

    def insert_or_abort(self, appt):
        time_str = str(appt['time'])
        if appt['time'].minute % 15 != 0:
            abort(
                400, message="Appointment time must be in 15 minute intervals: {}".format(time_str))
        if not self.can_accommodate(time_str):
            abort(400, message="Appointment time full: {}".format(time_str))

        self.id_store[appt['id']] = appt
        if time_str not in self.datetime_store:
            self.datetime_store[time_str] = []
        self.datetime_store[time_str].append(appt['id'])

    def remove(self, appt_id):
        time_str = str(self.fetch_by_id_or_abort(appt_id)['time'])
        self.datetime_store[time_str] = \
            filter(lambda id: id != appt_id, self.datetime_store[time_str])
        del self.id_store[appt_id]


class Appointment(Resource):
    def __init__(self, **kwargs):
        self.store = kwargs['store']

    def get_appt_store(self, doctor_id):
        if doctor_id not in self.store:
            abort(404, message="Doctor {} doesn't exist".format(doctor_id))
        return self.store[doctor_id]['appointments']

    @marshal_with(appointment_fields)
    def get(self, doctor_id, appt_id):
        return self.get_appt_store(doctor_id).fetch_by_id_or_abort(appt_id)

    def delete(self, doctor_id, appt_id):
        self.get_appt_store(doctor_id).remove(appt_id)
        return '', 204


class AppointmentList(Resource):
    def __init__(self, **kwargs):
        self.store = kwargs['store']
        self.next_id = 0

    def get_appt_store(self, doctor_id):
        if doctor_id not in self.store:
            abort(404, message="Doctor {} doesn't exist".format(doctor_id))
        return self.store[doctor_id]['appointments']

    @marshal_with(appointment_fields)
    def get(self, doctor_id):
        appt_store = self.get_appt_store(doctor_id)
        if 'date' in request.args:
            date = parse_date_str_or_abort(str(request.args['date']), '%Y-%m-%d').date()
            return appt_store.fetch_by_date(date)
        return appt_store.fetch_all()

    @marshal_with(appointment_fields)
    def post(self, doctor_id):
        global NEXT_ID
        args = parser.parse_args()
        time = parse_date_str_or_abort(str(args['time']), '%Y-%m-%dT%H:%M')
        appt = {
            'id': NEXT_ID,
            'kind': args['kind'],
            'time': time,
            'patient': args['patient']
        }
        self.get_appt_store(doctor_id).insert_or_abort(appt)
        NEXT_ID += 1
        return appt, 201
