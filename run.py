from app import app
from db import db


import auth
app.register_blueprint(auth.bp)
import dashboard
app.register_blueprint(dashboard.bp)


@app.before_first_request
def create_table():
    db.create_all()
    # delete message when scheduled message is executed
    db.session.execute(
        'create trigger if not exists after delete on apscheduler_jobs BEGIN delete from messages where id=old.id; END;')
    db.session.execute(
        'create trigger if not exists after delete on groups BEGIN delete from telegram where group_fk = old.id; END;'
    )
    db.session.execute(
        'create trigger if not exists after delete on groups BEGIN delete from whatsapp where group_fk = old.id; END;'
    )
    db.session.execute(
        'create trigger if not exists after delete on whatsapp BEGIN delete from groups where id=old.group_fk; END;'
    )
    db.session.execute(
        'create trigger if not exists after delete on telegram BEGIN delete from groups where id=old.group_fk; END;'
    )
    db.session.commit()
    db.session.close()
