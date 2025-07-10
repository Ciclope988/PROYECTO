# gmail_client.py
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

class GmailClient:
    def __init__(self):
        self.creds = None
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send'] 
        
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Cliente de Gmail configurado exitosamente.")

    def get_latest_emails(self, num_emails=5):
        """Obtiene los últimos N correos electrónicos no leídos de la bandeja de entrada."""
        try:
            results = self.service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
            messages = results.get('messages', [])

            emails_data = []
            if not messages:
                print("No se encontraron correos no leídos.")
                return []
            else:
                print(f"Se encontraron {len(messages)} correos no leídos.")
                for message in messages[:num_emails]:
                    msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                    
                    headers = msg['payload']['headers']
                    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                    sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No Sender')

                    body_html = None
                    body_text = None

                    if 'parts' in msg['payload']:
                        for part in msg['payload']['parts']:
                            if part['mimeType'] == 'text/plain':
                                if 'data' in part['body']:
                                    body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            elif part['mimeType'] == 'text/html':
                                if 'data' in part['body']:
                                    body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    else: # Si el cuerpo no tiene partes, es un mensaje simple
                        if 'data' in msg['payload']['body']:
                            body_text = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

                    emails_data.append({
                        "id": message['id'],
                        "subject": subject,
                        "from": sender,
                        "body_html": body_html,
                        "body_text": body_text
                    })
                    
                    # Marcar el correo como leído después de procesarlo
                    self.service.users().messages().modify(
                        userId='me', 
                        id=message['id'], 
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    print(f"Correo '{subject}' de '{sender}' marcado como leído.")
            return emails_data
        except HttpError as error:
            print(f"Ocurrió un error al obtener correos: {error}")
            return []

    def send_email(self, sender_email, to_email, subject, message_text, in_reply_to_id=None):
        """
        Envía un correo electrónico.
        sender_email: La dirección de correo del remitente ('me' o tu correo real).
        to_email: La dirección de correo del destinatario.
        subject: El asunto del correo.
        message_text: El cuerpo del correo.
        in_reply_to_id: El Message-ID del correo original para responder en hilo.
        """
        try:
            message = MIMEText(message_text)
            message['to'] = to_email
            message['from'] = sender_email
            message['subject'] = subject
            
            if in_reply_to_id:
                # Si el ID ya tiene los <> se usa directamente, si no, se añaden.
                if not in_reply_to_id.startswith('<') and not in_reply_to_id.endswith('>'):
                    in_reply_to_id = f"<{in_reply_to_id}>"
                message['In-Reply-To'] = in_reply_to_id
                message['References'] = in_reply_to_id # Añadir References para un mejor threading

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            
            print(f"Correo enviado a {to_email}. Message Id: {sent_message['id']}")
            return sent_message # Retorna la información del mensaje enviado
        except HttpError as error:
            print(f"Error al enviar correo: {error}")
            return None # Retorna None en caso de error