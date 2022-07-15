# -*- coding: utf-8 -*-
# coding=gbk
import os
import database
from io import BytesIO

from flask import Flask, render_template, request, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pdfCropMargins import crop

crop(["-p", "20", "-u", "-s", "paper1.pdf"])
crop(["-p", "0", "-gui", "paper2.pdf"])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        upload = Upload(filename=file.filename, data=file.read())
        db.session.add(upload)
        db.session.commit()
        f"Uploaded: {file.filename}"
        uploaded_files = request.files["file"]
        uploaded_files.save("static/pdf_file/{}".format(file.filename))
        database.save(file.filename)
    return render_template('index.html')


@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    return render_template('upload_pdf.html')


@app.route("/upload_done", methods=["POST"])
def upload_done():
    house_list = database.load_list()
    length = len(house_list)
    return render_template("upload_done.html", house_list=house_list, length=length)


@app.route("/download/<upload_id>/")
def download(upload_id):
    upload = Upload.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
        app.run()
