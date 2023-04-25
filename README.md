# Django Boilerplate

This repository is a simple boilerplate for quick starting Django with its basic settings.

Pull/clone this repository and get started as follows.

---

## Getting Started

1. Install Python >=3.3
2. Create a virtualenv using `virtualenv env`
3. Start your virtualenv using `source ./env/bin/activate`
4. Install dependencies using `pip install -r requirements.txt`
5. Set your **script** file in `scripts/config.json`, for example:
```json
    {
        "SECRET_KEY": "your-secret-key",
        "LANGUAGE_CODE": "pt-br",
        "TIME_ZONE": "America/Sao_Paulo",
        "ENVIRONMENT": "development"
    }
```
6. Make (after configure your database) the initial migration using `python3 manage.py migrate`
7. Rename your project using `python3 manage.py renameproject.py djangoBoilerplate <new_project_name>`
8. Run the server using `python3 manage.py runserver`.