from datetime import datetime
import json
import logging
import os

from flask import Flask, render_template, request, session, send_file
from werkzeug.utils import secure_filename

from src.finance.benchmark import Benchmark, TICKERFILE

import sys
path = '/home/jbhangoo/mysite'
if path not in sys.path:
   sys.path.insert(0, path)

from src.ebird.ebird import EbirdApi

logdir = os.path.join(os.getcwd(), "data", "_logs")

app = Flask(__name__)
app.config.from_object('config')
database_file = app.config['DATABASE_PATH']
app.secret_key = app.config["SECRET_KEY"]

# Logger
if not os.path.exists(logdir):
    os.mkdir(logdir)
logfilename = "ebird_{0}.log".format(datetime.today().strftime('%Y%m%d_%H%M%S'))
logfilepath = os.path.join(logdir, logfilename)

logging.basicConfig(filename = logfilepath, level=logging.ERROR, format = f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

@app.route("/", methods = ['GET', 'POST'])
def root():
    req = {
        "lat": 32.2,
        "lon": -110.9,
        "region": "Pima",
        "radius": 5,
        "days": 7,
        "notable": "0",
        "species": ''
    }
    ebird = EbirdApi(req)
    return render_template("index.html", obs=ebird.locSpecies.locations)

@app.route("/finance/")
def finance():
    benchmark = Benchmark()
    charts = benchmark.get_charts()
    return render_template("finance.html", graphJSON=charts)

@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/load/", methods = ['GET'])
def load():
    try:
        app.logger.debug("START Loading")
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = int(float(request.args.get('diam'))//2000)
        radius -= 1
        if (radius < 1) or (radius > 50):
            raise Exception("Invalid search area")
        days = int(request.args.get('days'))
        req = {
            "lat": lat,
            "lon": lon,
            "region": "Pima",
            "radius": radius,
            "days": days,
            "notable": "0",
            "species": ''
        }
        ebird = EbirdApi(req)
        return ebird.locSpeciesJson
    except Exception as ex:
        errmsg = []
        errmsg.append(str(ex))
        return json.dumps(errmsg);


@app.errorhandler(401)
def hdlr_401(error):
    return render_template("page_401.html"), 401

@app.errorhandler(403)
def hdlr_403(error):
    return render_template("page_403.html"), 403

@app.errorhandler(404)
def hdlr_404(error):
    return render_template("page_404.html"), 404

@app.errorhandler(405)
def hdlr_405(error):
    return render_template("page_405.html"), 405

@app.errorhandler(413)
def hdlr_413(error):
    return render_template("page_413.html"), 413

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8022)
