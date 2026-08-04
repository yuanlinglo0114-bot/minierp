from flask import Flask

from app import db as db_module
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_module.init_app(app)

    from app.main import bp as main_bp
    from app.product import bp as product_bp
    from app.employee import bp as employee_bp
    from app.inbound import bp as inbound_bp
    from app.outbound import bp as outbound_bp
    from app.reports import bp as reports_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix="/product")
    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(inbound_bp, url_prefix="/inbound")
    app.register_blueprint(outbound_bp, url_prefix="/outbound")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    return app
