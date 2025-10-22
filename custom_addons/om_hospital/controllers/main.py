from odoo import http
from odoo.http import request


class HospitalController(http.Controller):

    # Example 1: Basic page route
    @http.route("/hospital/hello", auth="public", type="http")
    def hello_world(self, **kwargs):
        return "<h1>Hello from Odoo Controller!</h1>"

    # Example 2: JSON API route
    @http.route("/hospital/patients", auth="public", type="json", csrf=False)
    def list_patients(self, **kwargs):
        patients = request.env["hospital.patient"].sudo().search([])
        return [{"id": p.id, "name": p.name, "age": p.age} for p in patients]

    # Example 3: Route with parameters
    @http.route("/hospital/patient/<int:patient_id>", auth="public", type="http")
    def show_patient(self, patient_id):
        patient = request.env["hospital.patient"].sudo().browse(patient_id)
        if not patient.exists():
            return "<h2>Patient not found</h2>"
        return f"<h2>Patient Name: {patient.name}</h2><p>Age: {patient.age}</p>"
