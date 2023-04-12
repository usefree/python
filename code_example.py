import requests, json, datetime


ELASTIC = 'http://192.168.0.51:9200/'
KIBANA_URL = "https://kibana.domain.com/"
INDEX = 'logs.tti-' + (datetime.date.today()).strftime("%Y.%m.%V")
TIME = '15m'
MESSAGE = ""
KNOWN_ERRORS=[]
KNOWN_ERRORS.append('Microsoft.AspNetCore.Server.Kestrel.Core.BadHttpRequestException: Reading the request body timed out due to data arriving too slowly. See MinRequestBodyDataRate.')
KNOWN_ERRORS.append('Receive failed: Connection reset by peer, Code=Local_Transport, IsBrokerError=False, IsLocalError=True')
KNOWN_ERRORS.append('After applying the update, the (immutable) field ')
KNOWN_ERRORS.append('OPTIMISTIC_CONCURRENCY')
URL = ELASTIC + INDEX + "/_search?pretty"
def addTemplate(time):
    template = json.loads("""
{
        "from": 0,
        "size": 100,
        "sort": [{
                "@timestamp": {
                        "order": "desc",
                        "unmapped_type": "boolean"
                }
        }],
        "aggs": {
                "2": {
                        "date_histogram": {
                                "field": "@timestamp",
                                "interval": "30s",
                                "time_zone": "Europe/Kiev"
                        }
                }
        },
"query": {
    "bool": {
      "must": [
        {
          "match_phrase": {
            "Level": {
              "query": "Error"
            }
          }
        },
        {
          "match_phrase": {
            "Properties.env": {
              "query": "Prod"
            }
          }
        },
        {
          "match_phrase": {
            "Properties.product": {
              "query": "app1"
            }
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-72h"
            }
          }
        }
      ]
    }
  }
}
   """)
    template['query']['bool']['must'][3]['range']['@timestamp']['gte'] = "now-"+time
    template = json.dumps(template)
    return template


def webRequest(url,data):
    timeout = 30
    try:
        response = requests.post(url, data=data, timeout=timeout)
    except Exception as e:
        return False
    else:
        return response.json()

def slack(message,query,startTime,endTime):
    kibana_url = 'http://kibana.domain.com/app/kibana#/discover?_g=()&_a=(columns:!(_source),index:AWcOTg_BBSSsXTo-ed9W,interval:auto,query:(query_string:(query:\'Properties.product:%22app1%22%20AND%20Properties.env:%22Prod%22%20AND%20Level:Error\')),sort:!(\'@timestamp\',desc))'
    data = json.dumps({'channel': "l1_notification",'text': '*TT There are errors in logs! app1 Prod*','attachments':[{'color':'#F78181', 'title': 'Error stack trace:', 'text': message, "fields": [{"title":"Link to kibana for details" ,"value": '<' + kibana_url + '|  http://kibana.domain.com>'  }]}], 'icon_emoji':':warning:'})
    # my test url
    url = 'https://hooks.slack.com/services/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'
    requests.post(url, data)

def CheckIfKnown(Message):
    print('new check if known error -------------------')
    answers = 'False'
    for Element in KNOWN_ERRORS:
        if Message.find(Element) == -1:
            print('Known error text -----------------------------------------------------------')
            print(Element)
            print('message -----------------------------------------------------------')
            print(Message)
            print ('Current known error text not found in message')
        else:
            print('Known error text -----------------------------------------------------------')
            print(Element)
            print('message -----------------------------------------------------------')
            print(Message)
            print ('Current known error text found in message')
            answers = 'True'
            return True
    return answers

def Main():
    template = addTemplate(TIME)
    request = webRequest(URL,template)
    send = []
    tosend = 'no'
    if request['hits']['total'] > 0:
        count = request['hits']['total']
        timeArray = []
        hits = request['hits']['hits']
        for hit in hits:
            timeArray.append(hit['_source']['@timestamp'])

        if count>0:
            for hit in hits:
                if CheckIfKnown(hit['_source']['message']) <> True:
                    print('Should it be sent? yes')
                    send.append('yes')
                    MESSAGE = hit['_source']['message']
                    print('MESSAGE to send -----------------------------')
                    print(MESSAGE)
                    print('MESSAGE to send /////-----------------------------')
                else:
                    send.append("no")
                    print('Should it be sent? no')
        print('To send or not to send (if at least one "yes" - to send)')
        for s in send:
            print('send? ----------------------------------')
            print(s)
            if s == 'yes':
                tosend = 'yes'

        print('Final solution - send message?--------------')
        print(tosend)
        if tosend == 'yes':
            slack("{} errors have occured for last {}!\n *Last error:*\n {}".format(count, TIME, MESSAGE), "*", timeArray[-1], timeArray[0])
#               print(count)

Main()
