""" This the heart of the application. From here
the application gets configured and build. """

from .database import db
from .models import User, Group, Role


def configure_logging(app):
    from flask import jsonify, has_request_context, request
    import sys, traceback
    from flask_security import current_user
    import logging
    root = logging.getLogger()
    if app.config['LOG_SENTRY_ACTIVE']:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        sentry_sdk.init(
            dsn=app.config['LOG_SENTRY_DSN'],
            integrations=[FlaskIntegration(),SqlalchemyIntegration()],
            traces_sample_rate=1.0
        )
    if app.config['LOG_MAIL_ACTIVE']:
        from .logger import ThreadedSMTPHandler
        mailhost = app.config['LOG_MAIL_HOST']
        port = app.config['LOG_MAIL_PORT']
        fromaddr = app.config['LOG_MAIL_FROM_ADDRESS']
        toaddrs = app.config['LOG_MAIL_TO_ADDRESS']
        username = app.config['LOG_MAIL_USERNAME']
        password = app.config['LOG_MAIL_PASSWORD']
        mail_handler = ThreadedSMTPHandler(
            mailhost=(mailhost, port),
            fromaddr=fromaddr,
            toaddrs=toaddrs,
            credentials=(username,password),
            subject='Application Error')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    if app.config['LOG_DATABASE_ACTIVE']:
        from .logger import SQLAlchemyHandler
        database_handler = SQLAlchemyHandler()
        database_handler.setLevel(logging.ERROR)
        app.logger.addHandler(database_handler)

    @app.errorhandler(500)
    def internal_server_error(error):
        original_error = getattr(error, "original_exception", None)
        handled_error = False
        if original_error is None:
            handled_error = True
        template = 'User uuid:{}\nIP:{}\nRequested URL:{}\nTraceback:{}'
        request_remote_addr = request_url = user_uuid = 'Unknown'
        post = False
        if has_request_context():
            request_url = request.url
            request_remote_addr = request.remote_addr
            if request.method == 'POST':
                post = True
            if current_user.is_authenticated:
                user_uuid = current_user.uuid
        admin_error_message = template.format(
                user_uuid,
                request_remote_addr,
                request_url,
                traceback.format_exc())
        app.logger.error(admin_error_message)
        template = 'An exception of type {0} occurred. Description:\n{1}'
        user_error_message = template.format(error.name, error.description)
        if handled_error:
            if post:
                return jsonify('The error has already been handled'), 500
            return 'The error has already been handled', 500
        if post:
            return jsonify(user_error_message), 500
        return user_error_message, 500
    return None

def init_extensions(app):
    from .database import db
    from .models import User, Group, Role
    from flask_security import SecurityManager, UserDatastore
    user_datastore = UserDatastore(db, User, Group, Role)
    security_manager = SecurityManager(app, user_datastore)


def init_vendors(app):
   # from .database import db
    db.init_app(app)
    db.create_all()


def register_blueprints(app):
    from werkzeug.utils import find_modules, import_string
    for name in find_modules(__name__, include_packages=True, recursive=True):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None


def run_migration(app):
   # from application.database import db
    from flask_migrate import Migrate
    return Migrate(app, db)


def setup_db_defaults(app):
    @app.before_first_request
    def db_setup():
        if not app.config['DB_DEFAULT_VALUES_ACTIVE']:
            return None
        import confuse
        from sqlalchemy import exc
   #     from .database import db
   #     from .models import User, Group, Role
        config = confuse.Configuration('NamTech', __name__)
        config.set_file('database.yaml')
        nested_dict = config['db-defaults'].get()
        if not nested_dict:
            return None
        for model, nested_value_list in nested_dict.items():
            if not model in locals():
                continue
            Model = locals()[model]
            for value_dict in nested_value_list:
                model = Model()
                conditions = []
                for key, value in value_dict.items():
                    conditions.append(getattr(Model, key) == value)
                    setattr(model, key, value)
                exists = db.session.query(Model).filter(db.and_(*conditions)).scalar()
                if exists:
                    continue
                try:
                    db.session.add(model)
                    db.session.commit()
                except exc.SQLAlchemyError as e:
                    db.session.rollback()
                    app.logger.error(e.orig)


def create_app(env=''):
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object('config.Config' + env)
    configure_logging(app)
    with app.app_context():
        register_blueprints(app)
        init_extensions(app)
        init_vendors(app)
        run_migration(app)
        setup_db_defaults(app)
        return app
