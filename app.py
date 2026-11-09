"""Punto de entrada de la app Flask.

Crea la app, registra el Blueprint de polizas y la ejecuta.
"""

from flask import Flask

from controllers.polizas_controller import polizas_bp

app = Flask(
    __name__,
    template_folder="views",
    static_folder="public/static",
    static_url_path="/static",
)

app.register_blueprint(polizas_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
