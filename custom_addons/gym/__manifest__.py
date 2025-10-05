{
    "name": "Gym Management System",
    "version": "1.0.0",
    "category": "Gym Management",
    "description": "Gym Management",
    "sequence": -101,
    "depends": ["mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/trainer_view.xml",
        "views/trainee_view.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
