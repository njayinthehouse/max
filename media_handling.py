import requests
from os import listdir, path, remove
from reportlab.platypus import SimpleDocTemplate, Image, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


def download_image(url, directory, name):
    r = requests.get(url)
    extension = url.split('.')[-1]
    img_path = path.join(directory, '{0}.{1}'.format(name, extension))
    f = open(img_path, 'wb')

    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()

    return img_path


def download_images(images, directory):
    image_paths = []

    print 'Downloading...'
    for i, image in enumerate(images):
        img = download_image(url=image, directory=directory, name=i)
        image_paths.append(img)

    return image_paths


def dump_images(directory):
    images = [path.join(directory, f) for f in listdir(directory) if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.jpeg')]
    for image in images:
        remove(image)


def generate_pdf(images, directory, name):
    file_name = path.join(directory, '{0}.pdf'.format(name))
    doc = SimpleDocTemplate(file_name, pagesize=letter, rightMargin=72,
                            leftMargin=72, topMargin=72, bottomMargin=18)
    story = []
    width = 7.5 * inch
    height = 9.5 * inch

    print 'Generating PDF...'
    for picture in images:
        image = Image(picture, width, height)
        story.append(image)
        story.append(PageBreak())

    doc.build(story)
    return file_name