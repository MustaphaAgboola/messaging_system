from flask import Flask, request, jsonify
from celery import Celery
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'pyamqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

# Set up logging
logging.basicConfig(filename='/var/log/messaging_system.log', level=logging.INFO)

@celery.task
def send_email_task(to_email):
    smtp_server = "smtp.your_email_provider.com"
    smtp_port = 587
    smtp_username = "your_username"
    smtp_password = "your_password"
    from_email = "your_email@your_domain.com"

    subject = "Test Email"
    body = "This is a test email sent using Celery and Flask."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, [to_email], msg.as_string())
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

@app.route('/endpoint', methods=['GET'])
def handle_request():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')
    response = {}

    if sendmail:
        send_email_task.apply_async(args=[sendmail])
        response['sendmail'] = f"Email task queued to: {sendmail}"
    
    if talktome:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"talktome parameter received at: {current_time}")
        response['talktome'] = "Current time logged."

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
