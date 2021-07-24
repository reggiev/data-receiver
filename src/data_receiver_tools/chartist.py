from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def parser_correlating_alert(msg):
  data = {}
  metrics = ["Symbol", "Identified time", "Breakout price", "Forecast price", "Forecast pips"
          "Probability", "Pattern", "Interval", "Probability", "Forecast pips"]

  prev_pattern_value = ""
  data["patterns"] = []

  sb = BeautifulSoup(msg["html"], 'html.parser')
  for a in sb.select("table table tr td"):
    if a.get_text():
        r = a.get_text()
        j = r.replace("\n", "").replace("Direction: ", "").replace(u'\xa0', u' ')
        j = j.replace("\t\t", "").replace(" \t", " ").split("\n")

        for b in j:
            c = b.split("\t")

            for v in c:
              # Split it on the first semicolon
              t = v.split(":", 1)
              key = t[0].strip(" ")

              if len(t) !=2 or key not in metrics:
                  continue

              if key == "Identified time":
                  # ADD 6 hours here to convert the CST time to UTC
                  # TODO a bug here for daylight savings
                  value = datetime.strptime(t[1].strip(" "), "%Y-%m-%d %H:%M CST") + timedelta(hours=6)
              elif key == "Date":
                  #TODO not sure on the timezone here
                  key = "Email Date"
                  value = datetime.strptime(t[1].strip(" ")[5:], "%b %d, %Y at %I:%M %p") - timedelta(hours=8)
              elif key in ["Breakout price", "Forecast pips", "Forecast price"]:
                  value = float(t[1].strip(" ").replace(",", ""))
              elif key == "Probability":
                  value = float(t[1].strip(" ").replace("%", "").replace(",", ""))
              elif key == "Pattern":
                  prev_pattern_value = t[1].strip(" ")
                  continue
              elif key == "Interval":
                  data["patterns"].append((prev_pattern_value, t[1].strip(" ")))
                  continue
              else:
                  value = t[1].strip(" ").strip(">").strip("<")
              data[key] = value
    
  if "Down.PNG" in msg["html"]:
    data["direction"] = "DOWN"
  elif "Up.PNG" in msg["html"]:
    data["direction"] = "UP"
  
  data["_id"] = msg["headers"]["message_id"]
  data["from"] = msg["headers"]["from"]
  data["date"] = msg["headers"]["date"]
  data["subject"] = msg["headers"]["subject"]
  data["to"] = msg["headers"]["to"]
  
  return [data]