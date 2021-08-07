from datetime import datetime
import os
import json

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from logging.config import dictConfig
from werkzeug.security import check_password_hash

from src.stateful_connectors.slack_connector import send_msg_to_slack_channel
from src.stateful_connectors.rabbitmq_connector import rmqwriter
from src.general_tools.encryptor import encrypt
from src.data_receiver_tools.chartist import parser_correlating_alert
 
app = Flask(__name__)
auth = HTTPBasicAuth()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(levelname)s] [%(module)s]: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


@auth.get_user_roles
def get_user_roles(user):
  # TODO log indirect user reference here, do not log user name
  app.logger.info("Returning access rights {} for {}.".format(user["user"], user["rights"]))
  return user["rights"]


@auth.verify_password
def verify_password(username, password):
  # TODO perform more sophisticated credentials verification
  # TODO store this is a more secure manner
  users = json.loads(os.environ.get('UML', ""))
  
  if username in users:
    if check_password_hash(users[username]["hash"], username+password):
      rmqwriter("e_sem", "sem", encrypt("[SUCCESS_AUTH] {}, IP: {}, DT: {}".format(username, request.remote_addr, datetime.now())))
      return {"user": username, "rights": users[username]["rights"]}
    else:
      rmqwriter("e_sem", "sem", encrypt("[INCORRECT_PASSWORD] {}, IP: {}, DT: {}".format(username, request.remote_addr, datetime.now())))
      app.logger.info("User failed to fully match for: {}".format(username))
  else:
    rmqwriter("e_sem", "sem", encrypt("[UNKNOWN_USER] {}, IP: {}, DT: {}".format(username, request.remote_addr, datetime.now())))
    app.logger.info("User failed login attempt for: {}".format(username))
  return False

 
@app.route('/')
def index():
  # TODO create a dashboard here? 
  return '<h1>Testing flask app</h1>'
  

@app.route('/api-request/chartist-email', methods=['POST'])
@auth.login_required(role=["user", ["chartist"]])
def chartist_email_interface():
  # parse the important data from the payload
  emsg = request.get_json(force=True)
  if "Correlating Alert" in emsg["headers"]["subject"]:
    parsed_data = parser_correlating_alert(emsg)
    en = encrypt(parsed_data)
    rmqwriter("e_prospects", "prospects", en)
  else:
    send_msg_to_slack_channel("slack_debug_msgs", {"text": "The subject is not yet supported: " + emsg["headers"]["subject"]})
  return "Ack"


@app.route('/api-request/pinger', methods=['POST'])
@auth.login_required(role=["user", ["pinger"]])
def ping_receiver():
  emsg = request.get_json(force=True)
  if not emsg["headers"]["subject"] == "Pinger msg":
    send_msg_to_slack_channel("slack_debug_msgs", {"text": "Unknown ping format received."})
  return "Ack"


if __name__ == "__main__":
    # TODO run this cleaner in production
    send_msg_to_slack_channel("slack_process_monitor", {"text": "Starting the chartist listener."})
    app.run(host='0.0.0.0', port=os.environ.get('PORT', ""))
    
