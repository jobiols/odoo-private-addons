# -*- coding: utf-8 -*-
#################################################################################
#    Copyright (C) 2022  jeo Software  (http://www.jeosoft.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#################################################################################

{
    "name": "HR Attendance Face Recognition",
    "summary": "Permite hacer el checkin y checkout de empleados utilizando reconocimiento facial",
    "version": "13.0.1",
    "description": """
        Mediante algoritmo de reconocimiento facial este modulo permite fichar la entrada
        y salida de empleados.
    """,
    "author": "SAMS",
    "maintainer": "SAMS",
    "license" :  "Other proprietary",
    "website": "https:sams-ing.com",
    "images": ["images/attendance_face_recognition.png"],
    "category": "Employees",
    "depends": [
        "base",
        "hr",
        "hr_attendance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/res_users.xml",
        "views/hr_employee_views.xml",
        "views/res_config_settings.xml",
        "views/hr_attendance_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],
    "installable": True,
    "application": True,
    "pre_init_hook"        :  "pre_init_check",
}
