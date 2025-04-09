#!/bin/bash
export FLASK_APP="app:create_app"
export FLASK_ENV=development

flask db init
flask db migrate -m "init"
flask db upgrade

