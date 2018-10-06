from flask import Flask
from flask_restful import Api
from doctor import Doctor, DoctorList
from appointment import Appointment, AppointmentList


app = Flask(__name__)
api = Api(app)

# In memory datastore for doctors and appointments
# {doctor_id -> {..., appointments -> {}}}
DATA = {}

api.add_resource(Doctor, '/doctor/<int:id>', resource_class_kwargs={'store': DATA})
api.add_resource(DoctorList, '/doctors', resource_class_kwargs={'store': DATA})
api.add_resource(Appointment,
                 '/doctor/<int:doctor_id>/appointment/<int:appt_id>',
                 resource_class_kwargs={'store': DATA})
api.add_resource(AppointmentList,
                 '/doctor/<int:doctor_id>/appointments',
                 resource_class_kwargs={'store': DATA})

@app.errorhandler(404)
def not_found(e):
    return '', 404
