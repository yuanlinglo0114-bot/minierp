from flask import Flask, redirect, request, session, url_for

from app import db as db_module
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_module.init_app(app)

    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.product import bp as product_bp
    from app.employee import bp as employee_bp
    from app.doctype import bp as doctype_bp
    from app.warehouse import bp as warehouse_bp
    from app.customer import bp as customer_bp
    from app.vendor import bp as vendor_bp
    from app.inbound import bp as inbound_bp
    from app.outbound import bp as outbound_bp
    from app.reports import bp as reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix="/product")
    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(doctype_bp, url_prefix="/doctype")
    app.register_blueprint(warehouse_bp, url_prefix="/warehouse")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(vendor_bp, url_prefix="/vendor")
    app.register_blueprint(inbound_bp, url_prefix="/inbound")
    app.register_blueprint(outbound_bp, url_prefix="/outbound")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    @app.before_request
    def require_login():
        if request.endpoint in (None, "auth.login", "static"):
            return None
        if not session.get("authenticated"):
            return redirect(url_for("auth.login", next=request.path))
        return None

    @app.context_processor
    def inject_brand():
        return {"brand_name": app.config["BRAND_NAME"]}

    return app
