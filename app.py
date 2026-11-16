"""Punto de entrada de la app Flask.

Crea la app, registra el Blueprint de polizas y la ejecuta.
"""

import os
from flask import Flask

from controllers.polizas_controller import polizas_bp

app = Flask(
    __name__,
    template_folder="views",
    static_folder="public/static",
    static_url_path="/static",
    instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance"),
)

# Clave secreta para sesiones (cambiar en produccion por una variable de entorno)
app.secret_key = os.environ.get("SECRET_KEY", "dev-cambiar-en-produccion")

# Carpeta donde se guardan temporalmente los Excel importados por el usuario
app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # maximo 16 MB por archivo

app.register_blueprint(polizas_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
