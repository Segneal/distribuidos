"""
Email configuration for User Service using Nodemailer with Ethereal
"""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailConfig:
    """Email configuration class for Ethereal testing"""
    
    def __init__(self):
        # Ethereal SMTP configuration for testing
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.ethereal.email')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'ethereal.user@ethereal.email')
        self.smtp_password = os.getenv('SMTP_PASSWORD', 'ethereal.password')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@ong.com')
        self.from_name = os.getenv('FROM_NAME', 'Sistema ONG')
    
    def send_password_email(self, to_email, nombre_usuario, contraseña_temporal):
        """
        Send email with temporary password to new user
        
        Args:
            to_email (str): Recipient email address
            nombre_usuario (str): Username
            contraseña_temporal (str): Temporary password
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Bienvenido al Sistema ONG - Credenciales de Acceso"
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Create HTML content
            html_content = f"""
            <html>
              <body>
                <h2>Bienvenido al Sistema ONG</h2>
                <p>Hola <strong>{nombre_usuario}</strong>,</p>
                <p>Tu cuenta ha sido creada exitosamente. Aquí están tus credenciales de acceso:</p>
                <ul>
                  <li><strong>Usuario:</strong> {nombre_usuario}</li>
                  <li><strong>Email:</strong> {to_email}</li>
                  <li><strong>Contraseña temporal:</strong> {contraseña_temporal}</li>
                </ul>
                <p>Por favor, cambia tu contraseña después del primer inicio de sesión.</p>
                <p>Saludos,<br/>Equipo Sistema ONG</p>
              </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            Bienvenido al Sistema ONG
            
            Hola {nombre_usuario},
            
            Tu cuenta ha sido creada exitosamente. Aquí están tus credenciales de acceso:
            
            Usuario: {nombre_usuario}
            Email: {to_email}
            Contraseña temporal: {contraseña_temporal}
            
            Por favor, cambia tu contraseña después del primer inicio de sesión.
            
            Saludos,
            Equipo Sistema ONG
            """
            
            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            # Add HTML/plain-text parts to MIMEMultipart message
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            print(f"Email sent successfully to {to_email}")
            print(f"Preview URL: https://ethereal.email/message/{to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
            print("SMTP connection test successful")
            return True
        except Exception as e:
            print(f"SMTP connection test failed: {e}")
            return False

# Global email configuration instance
email_config = EmailConfig()