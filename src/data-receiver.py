import os
from datetime import datetime
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

from src.stateful_connectors.slack_connector import send_msg_to_slack_channel
from src.stateful_connectors.rabbitmq_connector import rmqwriter
from src.general_tools.encryptor import encrypt
from src.data_receiver_tools.chartist import parser_correlating_alert
 
app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
  # TODO perform more sophisticated credentials verification
  # TODO determine client access rights
  toks = os.environ.get("flask_token", "")
  print(toks)
  if check_password_hash(toks, username+password):
    return username
  else:
    # TODO send failed login event to rabbitMQ
    pass

 
@app.route('/')
def index():
  # TODO create a dashboard here? 
  return '<h1>Testing flask app</h1>'
  

@app.route('/api-request/chartist-email', methods=['POST'])
@auth.login_required
def chartist_email_interface():
  # parse the important data from the payload
  emsg = request.get_json(force=True)
  if "Correlating Alert" in emsg["headers"]["subject"]:
    parsed_data = parser_correlating_alert(emsg)
    en = encrypt(parsed_data)
    print(en)
    rmqwriter("e_prospects", "prospects", en)
  else:
    send_msg_to_slack_channel("slack_debug_msgs", {"text": "The subject is not yet supported: " + emsg["headers"]["subject"]})
  return "Ack"


@app.route('/api-request/pinger', methods=['POST'])
@auth.login_required
def ping_receiver():
  emsg = request.get_json(force=True)
  if not emsg["headers"]["subject"] == "Pinger msg":
    send_msg_to_slack_channel("slack_debug_msgs", {"text": "Unknown ping format received."})
  return "Ack"


if __name__ == "__main__":
    # TODO run this cleaner in production
    send_msg_to_slack_channel("slack_process_monitor", {"text": "Starting the chartist listener."})
    app.run(host='0.0.0.0', port=os.environ.get('PORT', ""))
    
