@echo off
python -m venv telco_churn
telco_churn\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r LP4_STAPP_Requirements.txt