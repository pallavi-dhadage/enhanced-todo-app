import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    try:
        smtp_host = os.environ.get('SMTP_HOST')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not all([smtp_host, smtp_user, smtp_password]):
            logger.warning('SMTP not configured, skipping email')
            return
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        logger.info(f'Email sent to {to_email}')
    except Exception as e:
        logger.error(f'Failed to send email: {e}')

def send_todo_reminder(email, template_type, context):
    """Send todo reminder emails"""
    templates = {
        'welcome': {
            'subject': 'Welcome to Enhanced Todo App!',
            'body': f"""
            <h1>Welcome {context['username']}!</h1>
            <p>Thank you for joining Enhanced Todo App. Start organizing your tasks today!</p>
            """
        },
        'reminder': {
            'subject': 'Todo Reminder: Tasks due soon',
            'body': f"""
            <h1>Todo Reminder</h1>
            <p>You have tasks due in the next 24 hours. Don't forget to complete them!</p>
            """
        }
    }
    
    template = templates.get(template_type)
    if template:
        send_email(email, template['subject'], template['body'])
