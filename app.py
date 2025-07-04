from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import datetime

app = Flask(__name__)

CERT_DIR = "generated_certificates"
os.makedirs(CERT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name']
    course = request.form['course']
    date = datetime.date.today().strftime("%d %B %Y")

    template = Image.open('static/certificate_template.png')
    draw = ImageDraw.Draw(template)
    img_width, img_height = template.size

    # Font setup
    font_path = "static/fonts/GreatVibes-Regular.ttf"
    if not os.path.exists(font_path):
        font_path = "arial.ttf"  # fallback

    name_font = ImageFont.truetype(font_path, 90)
    course_font = ImageFont.truetype(font_path, 80)
    date_font = ImageFont.truetype(font_path, 70)

    def center_text(draw, text, y, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img_width - text_width) // 2
        draw.text((x, y), text, font=font, fill='black')

    center_text(draw, name, y=620, font=name_font)
    center_text(draw, course, y=790, font=course_font)
    center_text(draw, date, y=890, font=date_font)

    # Save as PNG
    png_filename = f"{name.replace(' ', '_')}_certificate.png"
    png_filepath = os.path.join(CERT_DIR, png_filename)
    template.save(png_filepath)

    # Convert to PDF using reportlab
    pdf_filename = f"{name.replace(' ', '_')}_certificate.pdf"
    pdf_filepath = os.path.join(CERT_DIR, pdf_filename)

    c = canvas.Canvas(pdf_filepath, pagesize=A4)
    width, height = A4
    c.drawImage(png_filepath, 0, 0, width, height)  # full-page image
    c.save()

    return render_template('certificate.html', png_file=png_filename, pdf_file=pdf_filename)

@app.route('/download/png/<filename>')
def download_png(filename):
    return send_file(os.path.join(CERT_DIR, filename), as_attachment=True)

@app.route('/download/pdf/<filename>')
def download_pdf(filename):
    return send_file(os.path.join(CERT_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
