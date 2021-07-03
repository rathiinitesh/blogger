import os
import secrets
from flask_mail import Message

from PIL import Image
from flask import url_for, current_app

from blogger import mail


def save_file(image_uploaded):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(image_uploaded.filename)
    pic_filename = random_hex + file_ext
    pic_path = os.path.join(current_app.root_path, 'static/profile_pics', pic_filename)

    output_size = (125, 125)
    resized_image = Image.open(image_uploaded)
    resized_image.thumbnail(output_size)

    resized_image.save(pic_path)
    return pic_filename


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@bloggerdemo.com', recipients=[user.email])
    msg.body = f"""To reset your password visit the link below:

{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request, please just ignore this email and no changes will be made.
"""
    mail.send(msg)
