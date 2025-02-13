from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    
    # Verificar la conexión
    with app.app_context():
        try:
            # Intenta hacer una consulta simple
            result = db.session.execute(text('SELECT * FROM pasantes'))
            rows = [row for row in result]
            print("Conexión exitosa a la base de datos")
            print(f"Pasantes encontrados: {len(rows)}")
            for row in rows:
                print(f"Pasante: {row}")
        except Exception as e:
            print("Error al conectar con la base de datos:", str(e))
            print("Por favor verifica:")
            print("1. Que PostgreSQL esté corriendo")
            print("2. Que la base de datos bd_Clinica_Fisioterapia exista")
            print("3. Que el usuario postgres tenga la contraseña admin123")
            print("4. Que puedas conectarte usando: psql -U postgres -d bd_Clinica_Fisioterapia")

# Agregar esta función para verificar los pasantes
def verificar_pasantes():
    from models.pasante import Pasante
    pasantes = Pasante.query.all()
    print(f"Total de pasantes en la base de datos: {len(pasantes)}")
    for p in pasantes:
        print(f"Pasante: ID={p.id}, Nombre={p.nombre}")

# Llamar a esta función al iniciar la aplicación
def init_db(app):
    db.init_app(app)
    with app.app_context():
        verificar_pasantes()
