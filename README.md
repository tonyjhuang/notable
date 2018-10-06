To run:

1. clone repo
2. `mkvirtualenv notable`
3. `pip install -r requirements.txt`
4. `export FLASK_APP=run_app.py`
5. `flask run`


Endpoints:
1. `/doctors`: `GET`, `POST`
2. `/doctor/:id`: `GET`, `DELETE`
3. `/doctor/:id/appointments`: `GET`, `POST`
4. `/doctor/:id1/appointment/:id2`: `GET`, `DELETE`

