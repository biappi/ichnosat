from flask import Flask
app = Flask(__name__)
import pika
import subprocess
import json
import logging
import logger
import os
import downloader.start
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import database.db as db
from database.services.products_service import ProductsService
from database.entities.product import *
from scientific_processor.src.start import *




@app.route('/notify-scientific_processor')
def notify_scientific_processor():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')
    body_obj = {"source": "/usr/ichnosat/pre-processor/outbox/10SDG20151207_0/"}
    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=json.dumps(body_obj))
    print(" [x] Sent 'Hello World!'")
    connection.close()
    return "done"

@app.route('/start-scientific_processor')
def start_scientific_xs():
    logging.debug("[ichnosat-manager][]: Start scientific_processor")
    #start_scientific_processor()
    subprocess.Popen(["/bin/bash", "bash/start-scientific-processor.sh", "var=11; ignore all"])
    return "done"


@app.route('/processor')
def startproce_scientific_xs():
    logging.debug("[ichnosat-manager][]: Start scientific_processor")
    start_scientific_processor()
    logging.debug("")
    #subprocess.Popen(["/bin/bash", "bash/start_scientific-processor.sh", "var=11; ignore all"])
    return "done"


@app.route('/compile-plugins')
def compile_plugins():
    logging.debug("(ichnosat-manager): START compile scientific_processor plugins")
    dirnames = os.listdir('/usr/ichnosat/scientific_processor/src/plugins/')
    r = re.compile('^[^\.]')
    dirnames = filter(r.match, dirnames)

    for plugin_name in dirnames:
        try:
            completed_without_error = True
            logging.debug("(ichnosat-manager): START compile of scientific-plugin '" + plugin_name + "' plugin")
            p = subprocess.Popen(["/bin/bash", "bash/compile-plugins.sh", plugin_name, "var=11; ignore all"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

            for line in p.stdout.read().decode('utf-8').split("\n"):
                if (len(line) > 0):
                    logging.debug("(BASH - compile-plugins.sh): " + line)

            for line in p.stderr.read().decode('utf-8').split("\n"):
                if (len(line) > 0):
                    logging.debug("[ERROR] (BASH compile-plugins.sh): " + line)
                    completed_without_error = False

            if(completed_without_error):
                logging.debug("(ichnosat-manager): Completed compile " + plugin_name + " plugin")
            else:
                logging.debug("[ERROR] (ichnosat-manager): Failed compilation of scientific_processor plugin '" + plugin_name + "'")

        except ValueError:
            logging.debug(
                "[ERROR] (ichnosat-manager): Failed compilation of scientific_processor plugin '" + plugin_name + "'")

    logging.debug("(ichnosat-manager): COMPLETED compile scientific_processor plugins")

    return "Done"

@app.route('/start-rabbitmq')
def start_rabbitmq():
    subprocess.Popen(["/bin/bash", "bash/start-rabbitmq.sh", "var=11; ignore all"])
    return "done"

@app.route('/stop-rabbitmq')
def stop_rabbitmq():
    subprocess.Popen(["/bin/bash", "bash/stop-rabbitmq.sh", "var=11; ignore all"])
    return "done"

@app.route('/rabbitmq-version')
def version_rabbitmq():
    subprocess.Popen(["/bin/bash", "bash/rabbitmq-version.sh", "var=11; ignore all"])
    return "done"


@app.route('/network-test')
def network_test():
    subprocess.Popen(["/bin/bash", "bash/network-test.sh", "var=11; ignore all"])
    return "done"

@app.route('/start-downloader')
def start_downloader():
    logging.debug("start-downloder")
    downloader.start.start()
    return "started-download"



@app.route('/write-database', methods=['GET','POST'])
def add_database():
    ps = ProductsService()
    ps.add_new_product()
    return "added?"

@app.route('/read-database', methods=['GET','POST'])
def read_database():
    ps = ProductsService()
    logging.debug("|||||| show list of pending products ||||")
    for product in ps.get_pending_products():
        logging.debug(product)

    return "done"

@app.route('/database', methods=['GET','POST'])
def create_database():
    dd = db.DB()
    dd.create_db()
    return "Done"


@app.route('/update-database', methods=['GET','POST'])
def update_database():
    ps = ProductsService()
    ps.update_product_status("tiles/32/T/NL/2016/10/9/0/",ProductStatus.downloaded)

    return "done"


if __name__ == '__main__':
    logging.debug("START ")
    logging.debug("START RABBITMQ")
    #subprocess.Popen(["/bin/bash", "bash/start-rabbitmq.sh", "var=11; ignore all"])
    #logging.debug("START SCIENTIFIC PROCESSOR")
    #start_scientific_processor()

    app.run(debug=True,host='0.0.0.0')