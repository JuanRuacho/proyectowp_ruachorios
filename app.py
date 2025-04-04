from flask import (
    Config,
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flaskext.mysql import MySQL
from flask_mail import Mail, Message

app = Flask(__name__)

app.secret_key = "supersecretkey"
app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "misitio"


# Configura Mailtrap
# Looking to send emails in production? Check out our Email API/SMTP product!
app.config.from_object(Config)
mail = Mail(app)

app.config["MAIL_SERVER"] = "sandbox.smtp.mailtrap.io"
app.config["MAIL_PORT"] = 2525
app.config["MAIL_USERNAME"] = "3ca3198bd901cd"
app.config["MAIL_PASSWORD"] = "166626a3651dae"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


mysql = MySQL()
mysql.init_app(app)


@app.before_request
def reset_breadcrumbs():
    """Inicializa la lista de breadcrumbs, antes de cada peticion"""
    g.breadcrumbs = []
    print("Breadcrumbs inicializados:", g.breadcrumbs)


# Funcion para agregar breadcrumb
def add_breadcrumb(name, url):
    """Agrega un breadcrumb a la lista global"""
    g.breadcrumbs.append({"text": name, "url": url})
    print("Breadcrumbs agregados :", g.breadcrumbs)


# Pagina de inicio
@app.route("/")
# Funcion inicio con breadcrumbs
def index():
    add_breadcrumb("inicio", "/")

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    print("Usuarios:", data)  # Solo para depurar

    return render_template("sitio/index.html")


# Pagina de proyectos
@app.route("/acercade")
# Breadcrumb para proyectos
def acercade():
    add_breadcrumb("inicio", "/")
    add_breadcrumb("acerca de", "/acercade")
    return render_template("sitio/acercade.html")


# Pagina de proyectos
@app.route("/proyectos")
# Breadcrumb para proyectos
def proyectos():
    add_breadcrumb("inicio", "/")
    add_breadcrumb("proyectos", "/proyectos")
    return render_template("sitio/proyectos.html")


# Pagina de contacto
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    add_breadcrumb("inicio", "/")
    add_breadcrumb("contacto", "/contacto")
    if request.method == "POST":
        nombre = request.form["name"]
        correo = request.form["email"]
        mensaje = request.form["message"]
        msg = Message(
            "Nuevo mensaje de contacto",
            sender=correo,
            recipients=["ruacho73@gmail.com"],
        )
        msg.body = f"Nombre: {nombre}\nCorreo: {correo}\nMensaje:\n{mensaje}"
    return render_template("sitio/contacto.html")


@app.route("/send_email", methods=["POST"])
def send_mail():
    return render_template("contacto.html")


# Pagina de mapa del sitio
@app.route("/mapasitio")
def mapasitio():
    add_breadcrumb("inicio", "/")
    add_breadcrumb("mapa del sitio", "/mapasitio")
    return render_template("sitio/mapasitio.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        clave = request.form["clave"]

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE correo=%s AND clave=%s", (correo, clave)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            session["id"] = usuario[0]  # Guardamos el ID del usuario en sesión
            session["Nombre"] = usuario[1]
            session["correo"] = usuario[2]
            return redirect(url_for("index"))  # Redirige al index
        else:
            return render_template(
                "admin/login.html", error="Usuario o contraseña incorrectos"
            )

    return render_template("admin/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        clave = request.form["clave"]

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, clave) VALUES (%s, %s, %s)",
            (nombre, correo, clave),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("admin/register.html")


# Filtros personalizados
# @app.add_template_filter
# def today(date):
#    return date.strftime('%d-%m-%y')

if __name__ == "__main__":
    app.run(debug=True)
