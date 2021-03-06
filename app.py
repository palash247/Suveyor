from flask import Flask
from flask_restful import Api
from resourcess.update import Update
import os
from logging.config import dictConfig
from sqlalchemy import DDL, event
from models.schedule import ScheduleModel

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

TOKEN = os.environ.get('TELEGRAM_TOKEN')

app = Flask(__name__)
app.secret_key = 'palash'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/palash/surveyor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True


api = Api(app)


# @app.before_first_request
# def create_table():
#     db.create_all()
#     # delete message when scheduled message is executed
#     db.session.execute(
#         'create trigger if not exists after delete on apscheduler_jobs BEGIN delete from messages where id=old.id; END;')
#     db.session.execute(
#         'create trigger if not exists after delete on groups BEGIN delete from telegram where group_fk = old.id; END;'
#     )
#     db.session.execute(
#         'create trigger if not exists after delete on groups BEGIN delete from whatsapp where group_fk = old.id; END;'
#     )
#     db.session.execute(
#         'create trigger if not exists after delete on whatsapp BEGIN delete from groups where id=old.group_fk; END;'
#     )
#     db.session.execute(
#         'create trigger if not exists after delete on telegram BEGIN delete from groups where id=old.group_fk; END;'
#     )
#     db.session.commit()
#     db.session.close()

api.add_resource(Update, '/{}'.format(TOKEN))


if __name__ == '__main__':
    import auth
    app.register_blueprint(auth.bp)
    import dashboard
    app.register_blueprint(dashboard.bp)
    from db import db
    db.init_app(app)
    app.run(port=5000)
