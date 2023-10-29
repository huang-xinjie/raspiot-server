import hashlib
import os
import uuid

from flask import request, send_from_directory, current_app
from werkzeug import exceptions
from werkzeug.utils import secure_filename

from api import raspiot_api


def allowed_file(filename):
    return os.path.splitext(secure_filename(filename))[-1] in current_app.config['UPLOAD_ALLOWED_EXTENSIONS']


def file_seek(func):
    def wrap(file, *args, **kwargs):
        rst = func(file, *args, **kwargs)
        file.seek(0)
        return rst

    return wrap


@file_seek
def file_size(file):
    return len(file.read()) // 1024


@file_seek
def file_hash(file):
    return hashlib.md5(file.read()).hexdigest()


@raspiot_api.post('/upload')
def upload_file():
    file = request.files.get('file')
    if file and file.filename and allowed_file(file.filename):
        extension = os.path.splitext(secure_filename(file.filename))[-1]
        filename = f'{uuid.UUID(hex=file_hash(file))}{extension}'
        abs_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(abs_filepath):
            file.save(abs_filepath)
        return f'/uploads/{filename}'

    raise exceptions.BadRequest(description=f'filename {file.filename} is invalid, '
                                            f'only support {current_app.config["UPLOAD_ALLOWED_EXTENSIONS"]}')


@raspiot_api.get('/uploads/<filename>')
def uploaded_file(filename):
    uploads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads_path, filename)


@raspiot_api.get('/statics/<filename>')
def statics_file(filename):
    statics_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statics')
    return send_from_directory(statics_path, filename)

