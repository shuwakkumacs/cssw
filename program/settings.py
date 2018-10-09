from datetime import datetime

settings = {
    "YEAR": 2018,
    "WORKSHOP_DATE": datetime(2018, 10, 13),
    "COMMITTEE_CHAIR": {
        "email": "susumu@pcl.cs.waseda.ac.jp",
        "name": "斎藤奨",
        "name_en": "Susumu Saito",
        "lab": "小林",
        "lab_en": "Kobayashi",
        "grade": "D2"
    },
    "EXPIRATION": {
        "registration": True,
        "registration_date": datetime(2018, 9, 7, 23, 59, 59, 999999),
        "edit": True,
        "edit_date": datetime(2018, 9, 28, 23, 59, 59, 999999),
        "onsite": True,
        "onsite_date": datetime(2018, 10, 13, 23, 59, 59, 999999),
    },
    "SESSION_CATEGORIES": ["Technical", "Work-in-Progress", "Tmp"]
}
