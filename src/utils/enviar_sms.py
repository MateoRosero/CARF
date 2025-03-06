# enviar_sms.py
#import os
#from twilio.rest import Client
#from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
#load_dotenv()

#def enviar_sms(numero, mensaje):
    # Leer las credenciales de Twilio desde las variables de entorno
#    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
#    twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

    # Crear un cliente de Twilio
#    client = Client(account_sid, auth_token)

#    try:
        # Enviar el mensaje
#        message = client.messages.create(
#            body=mensaje,
#            from_=twilio_phone_number,
#            to=numero
#        )
#        return f"Mensaje enviado con éxito, SID: {message.sid}"
#    except Exception as e:
#        return f"Error al enviar el mensaje: {str(e)}"