from flask import Flask, render_template, request, redirect
import os
import numpy as np
import cv2
from matplotlib import pyplot as plt
from matplotlib import image as mpimage
import random
# Create the application.
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def hello():
    return render_template('index.html')

#app.config["IMAGE_UPLOADS"] = r"C:\Users\shrey\flaskapp\tmp"
app.config["IMAGE_UPLOADS"] = r"/static/images"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]

def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    return False

def countPieces(filename):
    img = cv2.imread(os.path.join(app.config["IMAGE_UPLOADS"], filename))
    print(os.path.join('/tmp', filename))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # gaussian transformation
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 255, 19)
    if thresh[0, 0] > 200:
        thresh = cv2.bitwise_not(thresh)
    # dilatation and erosion
    kernel = np.ones((1,1), np.uint8)
    img_dilation = cv2.dilate(thresh, kernel, iterations=1)
    img_erode = cv2.erode(img_dilation,kernel, iterations=1)
    # clean all noise after dilatation and erosion
    img_erode = cv2.medianBlur(img_erode, 7)

    ret, _ = cv2.connectedComponents(img_erode)
    print(ret-1)
    _, labels = cv2.connectedComponents(thresh)
    label_hue = np.uint8(random.randint(75, 200) * labels)
    blank_ch = 255 * np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
    labeled_img[label_hue == 0] = 0

    newfile = "edited." + filename.rsplit(".", 1)[1]
    #cv2.imwrite(os.path.join(app.config["IMAGE_UPLOADS"], newfile), labeled_img)
    try:
        os.remove(os.path.join(app.config["IMAGE_UPLOADS"], newfile))
    except: pass
    cv2.imwrite(os.path.join(app.config["IMAGE_UPLOADS"], newfile), labeled_img)
    return ret-1, newfile

@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if image.filename == "":
                print("Image must have a filename")
                return redirect(request.url)
            if not allowed_image(image.filename):
                print("Image filetype is not allowed")
                return redirect(request.url)
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            print("Saved successfully")
            n, newfile = countPieces(image.filename)
            #return render_template("image.html", user_image=os.path.join("/static/images", filename))
            return render_template("image.html", user_image=os.path.join("/static/images", image.filename), num=n, edited_image=os.path.join("/static/images", newfile))
    return render_template("upload_image.html")'''

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.debug = True
    app.run()
