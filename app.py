from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db():
    return psycopg2.connect(
        host="localhost",
        database="utn_db",
        user="postgres",
        password="root"
    )

@app.route("/")
def home():
    return "Backend funcionando OK"

# LOGIN
@app.route("/login", methods=["GET"])
def login():
    user = request.args.get("user")
    clave = request.args.get("pass")

    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM usuarios_utn WHERE usuario=%s AND clave=%s",
        (user, clave)
    )
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        if result["bloqueado"] == "Y":
            return jsonify({
                "respuesta": "ERROR",
                "mje": "Usuario bloqueado"
            })

        return jsonify({
            "respuesta": "OK",
            "mje": f"Ingreso Valido. Usuario {user}"
        })
    else:
        return jsonify({
            "respuesta": "ERROR",
            "mje": "Ingreso Invalido, usuario y/o clave incorrecta"
        })

# LISTA + BUSCAR + BLOQUEAR
@app.route("/lista", methods=["GET"])
def lista():
    action = request.args.get("action")

    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if action == "BUSCAR":
        usuario_filtro = request.args.get("usuario")

        if usuario_filtro:
            cursor.execute(
                "SELECT * FROM usuarios_utn WHERE usuario ILIKE %s ORDER BY id",
                ('%' + usuario_filtro + '%',)
            )
        else:
            cursor.execute("SELECT * FROM usuarios_utn ORDER BY id")

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)

    elif action == "BLOQUEAR":
        idUser = request.args.get("idUser")
        estado = request.args.get("estado")

        try:
            cursor.execute(
                "UPDATE usuarios_utn SET bloqueado=%s WHERE id=%s",
                (estado, idUser)
            )
            conn.commit()

            return jsonify({
                "respuesta": "OK",
                "mje": "Bloqueo Exitoso"
            })
        except Exception as e:
            return jsonify({
                "respuesta": "ERROR",
                "mje": str(e)
            })
        finally:
            cursor.close()
            conn.close()

    cursor.close()
    conn.close()
    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)