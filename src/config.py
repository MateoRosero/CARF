class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin123@localhost:5432/bd_Clinica_Fisioterapia'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'tu_clave_secreta'

    # Agregar logging para debug
    SQLALCHEMY_ECHO = True
