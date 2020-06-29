from flask import Flask,redirect,url_for,render_template,request,json
from sinling import SinhalaTokenizer
import requests
app = Flask(__name__,template_folder='template')

@app.route('/admin')
def hello_world():
    return render_template('index.html')

@app.route('/result/<result>')
def res(result):
    print(result)
    lyrics=json.loads(result)
    
    return render_template('home.html',result=lyrics['hits']['hits'])

@app.route('/admin',methods=['POST'])
def admin():
    text=request.form['qry']
    searchResults=json.dumps(getSearchResults(text))
    text=None;
    print(text)
    return redirect(url_for("res",result=searchResults));


def getSearchResults(text):
    reqJson={  "query": {    "multi_match" : {      "query":text,      "fields": [ "lyrics","artist"]     }  }}
    response=requests.get("http://localhost:9200/lyrics/_search",json=reqJson)
    return response.json()

# curl -XGET "http://localhost:9200/lyrics/_search" -H 'Content-Type: application/json' -d'{  "query": {    "multi_match" : {      "query":    "මිනිසුන්  ",      "fields": [ "lyrics"]     }  }}'