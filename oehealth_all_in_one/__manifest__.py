##############################################################################
#    Copyright (C) 2018 oeHealth (<http://oehealth.in>). All Rights Reserved
#    oeHealth, Hospital Management Solutions

# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, oeHealth.in, openerpestore.com, or if you have received a written
# agreement from the authors of the Software.
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

##############################################################################

{
    'name': 'oeHealth All In One',
    'version': '1.0',
    'author': "Braincrew Apps",
    'category': 'Generic Modules/Medical',
    'summary': 'Complete set of powerful features from oeHealth & oeHealth Extra Addons',
    'price': 220,
    'currency': 'EUR',
    'depends': ['base', 'sale', 'purchase', 'account', 'product','document','hr','web', 'account_invoicing'],
    'support': 'info@oehealth.in',
    'live_test_url': 'http://www.oehealth.in/demo',
    'description': """

About oeHealth
---------------

oeHealth is a multi-user, highly scalable, centralized Electronic Medical Record (EMR) and Hospital Information System for Odoo.

Manage your patients with their important details including family info, prescriptions, appointments, diseases, insurances, lifestyle,mental & social status, lab test details, invoices and surgical histories.

Administer all your doctors with their complete details, weekly consultancy schedule, prescriptions, inpatient admissions and many more.

Allow your doctors and patients to login inside your oeHealth system to manage their appointments. oeHealth is tightly integrated with Odoo’s calendar control so you will be always updated for your upcoming schedules.

""",
    "website": "http://oehealth.in",
    "data": [

        'views/oehealth.xml',

        'sequence/oeh_sequence.xml',
        'oeh_navigation.xml',
        'oeh_medical/views/res_partner_view.xml',
        'oeh_medical/views/product_product_view.xml',
        'oeh_medical/views/oeh_medical_medicaments_view.xml',
        'oeh_medical/views/oeh_medical_pharmacy_view.xml',
        'oeh_medical/views/oeh_medical_healthcenters_view.xml',
        'oeh_medical/views/oeh_medical_pathology_view.xml',
        'oeh_medical/views/oeh_medical_inpatient_view.xml',
        'oeh_medical/views/oeh_medical_view.xml',
        'oeh_medical/views/account_invoice_view.xml',
        'oeh_medical/views/oeh_medical_insurance_view.xml',
        'oeh_medical/views/oeh_medical_ethnic_groups_view.xml',
        'oeh_medical/views/oeh_medical_genetics_view.xml',
        'oeh_medical/data/oeh_physician_specialities.xml',
        'oeh_medical/data/oeh_physician_degrees.xml',
        'oeh_medical/data/oeh_insurance_types.xml',
        'oeh_medical/data/oeh_ethnic_groups.xml',
        'oeh_medical/data/oeh_who_medicaments.xml',
        'oeh_medical/data/oeh_dose_units.xml',
        'oeh_medical/data/oeh_drug_administration_routes.xml',
        'oeh_medical/data/oeh_drug_form.xml',
        'oeh_medical/data/oeh_dose_frequencies.xml',
        'oeh_medical/data/oeh_genetic_risks.xml',
        'oeh_medical/data/oeh_report_paperformat.xml',
        'oeh_medical/reports/report_patient_label.xml',
        'oeh_medical/reports/report_patient_medicines.xml',
        'oeh_medical/reports/report_appointment_receipt.xml',
        'oeh_medical/reports/report_patient_prescriptions.xml',
        'oeh_medical/views/oeh_medical_report.xml',

        'oeh_evaluation/views/oeh_medical_evaluation_view.xml',
        'oeh_socioeconomics/views/oeh_medical_socioeconomics_view.xml',
        'oeh_socioeconomics/data/oeh_occupations.xml',
        'oeh_gyneco/views/oeh_medical_gyneco_view.xml',
        'oeh_lifestyle/views/oeh_medical_lifestyle_view.xml',
        'oeh_lifestyle/data/oeh_recreational_drugs.xml',
        'oeh_lab/data/oeh_lab_test_units.xml',
        'oeh_lab/data/oeh_lab_test_types.xml',
        'oeh_lab/views/report_patient_labtest.xml',
        'oeh_lab/views/oeh_medical_lab_report.xml',
        'oeh_lab/views/oeh_medical_lab_view.xml',

        'oeh_pediatrics/views/res_partner_view.xml',
        'oeh_pediatrics/views/oeh_medical_pediatrics_newborn_view.xml',
        'oeh_pediatrics/views/oeh_medical_pediatrics_pcs_view.xml',
        'oeh_pediatrics/views/oeh_medical_pediatrics_growth_chart_view.xml',
        'oeh_pediatrics/data/oeh_medical_wfa_boys_p.xml',
        'oeh_pediatrics/data/oeh_medical_wfa_boys_z.xml',
        'oeh_pediatrics/data/oeh_medical_wfa_girls_p.xml',
        'oeh_pediatrics/data/oeh_medical_wfa_girls_z.xml',
        'oeh_pediatrics/data/oeh_medical_lhfa_boys_p.xml',
        'oeh_pediatrics/data/oeh_medical_lhfa_boys_z.xml',
        'oeh_pediatrics/data/oeh_medical_lhfa_girls_p.xml',
        'oeh_pediatrics/data/oeh_medical_lhfa_girls_z.xml',
        'oeh_pediatrics/data/oeh_medical_bmi_boys_p.xml',
        'oeh_pediatrics/data/oeh_medical_bmi_boys_z.xml',
        'oeh_pediatrics/data/oeh_medical_bmi_girls_p.xml',
        'oeh_pediatrics/data/oeh_medical_bmi_girls_z.xml',

        'oeh_icd10pcs/views/oeh_icd10pcs_view.xml',

        'oeh_surgery/views/oeh_medical_healthcenters_view.xml',
        'oeh_surgery/views/oeh_medical_surgery_view.xml',

        'oeh_ophthalmology/views/oeh_medical_ophthalmology_view.xml',
        'oeh_ophthalmology/views/oeh_medical_ophthalmology_report.xml',
        'oeh_ophthalmology/views/oeh_medical_report.xml',

        "oeh_nursing/views/oeh_medical_nursing_view.xml",
        "oeh_nursing/views/oeh_medical_rounding_report.xml",
        "oeh_nursing/views/oeh_medical_report.xml",

        "oeh_imaging/views/oeh_medical_imaging_view.xml",
        "oeh_imaging/views/report_patient_imaging.xml",
        "oeh_imaging/views/oeh_medical_imaging_report.xml",
        "oeh_imaging/data/oeh_imaging_test_types.xml",

        "oeh_evaluation_history/views/oeh_medical_evaluation_report.xml",
        "oeh_evaluation_history/views/oeh_medical_report.xml",

        'oeh_medical_certificate/views/oeh_medical_certificate_view.xml',
        'oeh_medical_certificate/views/report_medical_certificate.xml',
        'oeh_medical_certificate/views/oeh_medical_report.xml',

        'oeh_walkins/views/oeh_medical_register_for_walkin_view.xml',

        'oeh_patient_call_log/views/oeh_medical_patient_call_log_view.xml',

        'oeh_patient_medical_history/views/oeh_medical_patient_view.xml',

        'security/oeh_security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',

        'oeh_medical/data/oeh_disease_categories.xml',
        'oeh_medical/data/oeh_diseases.xml',

        'oeh_icd10pcs/data/oeh_icd_10_pcs_2009_part1.xml',
        'oeh_icd10pcs/data/oeh_icd_10_pcs_2009_part2.xml',
        'oeh_icd10pcs/data/oeh_icd_10_pcs_2009_part3.xml',

    ],
    "images": ['images/main_screenshot.png'],
    "demo": [

    ],
    'test':[
    ],
    'css': [],
    'js': [

    ],
    'qweb': [

    ],
    "active": False
}