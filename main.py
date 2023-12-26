from dotenv import load_dotenv
import os
from requests import post, get
import json
from flask import Flask, redirect, request, jsonify, session
from datetime import datetime, timedelta
import urllib.parse
import crearExcel

app=Flask(__name__)
app.secret_key='55555555d-5555555d-55555d'

load_dotenv()

client_id=os.getenv("CLIENT_ID")
client_secret=os.getenv("CLIENT_SECRET")
client_redirect_uri=os.getenv("REDIRECT_URI")
client_auth_url=os.getenv("AUTH_URL")
client_token_url=os.getenv("TOKEN_URL")
client_api_base_url=os.getenv("API_BASE_URL")



@app.route('/')
def index():
  return "Bienvenido a mi aplicacion de Spotify. <a href='/login'>Login with Spotify </a>"

@app.route('/login')
def login():
  scope='user-read-private user-read-email user-read-recently-played'
  params={
    'client_id':client_id,
    'response_type':'code',
    'scope':scope,
    'redirect_uri':client_redirect_uri,
    'show_dialog':True
  }
  auth_string=f"{client_auth_url}?{urllib.parse.urlencode(params)}"
  return redirect(auth_string)


@app.route('/callback')
def callback():
  if 'error' in request.args:
    return jsonify({"error":request.args['error']})
  if 'code' in request.args:
    req_body={
      'code': request.args['code'],
      'grant_type':'authorization_code',
      'redirect_uri':client_redirect_uri,
      'client_id': client_id,
      'client_secret':client_secret
    }

  response=post(client_token_url,data=req_body)
  token_info=response.json()
  session ['access_token']= token_info['access_token']
  session ['refresh_token']= token_info['refresh_token']
  session ['expires_at']= datetime.now().timestamp()+token_info['expires_in']

  return redirect ('/history')

@app.route('/history')
def get_history():
  if 'access_token' not in session:
    return redirect ('/login')

  if datetime.now().timestamp() > session ['expires_at']:
    return redirect ('/refresh-token')

  headers={
    "Authorization": f"Bearer {session ['access_token']}",
  }  
  response=get(client_api_base_url+"me/player/recently-played?limit=50",headers=headers)

  #history=response.json()

  json_result=json.loads(response.content)

  items = json_result["items"]
  songs_info = []
  for item in items:
      artists=[]
      for artist in item["track"]["artists"]:
        artist_name=artist["name"]
        artists.append(artist_name)
      id_track=item["track"]["id"]
      cancion={
        "id": item["track"]["id"],
        "name":item["track"]["name"],
        "artists":artists,
        "album":item["track"]["album"]["name"],
        "duration":item["track"]["duration_ms"],
        "popularity":item["track"]["popularity"],
        "explicit":item["track"]["explicit"],
      }
      response2=get(client_api_base_url+"audio-features/"+id_track,headers=headers)
      json_result2=json.loads(response2.content)
      cancion["acousticness"]=json_result2["acousticness"]
      cancion["danceability"]=json_result2["danceability"]
      cancion["energy"]=json_result2["energy"]
      cancion["instrumentalness"]=json_result2["instrumentalness"]
      cancion["key"]=json_result2["key"]
      cancion["liveness"]=json_result2["liveness"]
      cancion["loudness"]=json_result2["loudness"]
      cancion["mode"]=json_result2["mode"]
      cancion["speechiness"]=json_result2["speechiness"]
      cancion["tempo"]=json_result2["tempo"]
      cancion["valence"]=json_result2["valence"]
      songs_info.append(cancion)
      crearExcel.crearBD(songs_info)
      


  return songs_info





@app.route('/refresh-token')
def refresh_token():
  if 'refresh_token' not in session:
    return redirect ('/login')
  if datetime.now().timestamp() > session ['expires_at']:
    req_body={
      'grant_type': 'refresh_token',
      'refresh_token':   session ['refresh_token'],
      'client_id': client_id,
      'client_secret':client_secret
    }

    response=post(client_token_url,data=req_body)
    new_token_info=response.json()
    
    session ['access_token']= new_token_info['access_token']
    session ['expires_at']= datetime.now().timestamp()+new_token_info['expires_in']

  return redirect ('/history')

if __name__=='__main__':
  app.run(host='0.0.0.0', debug=True)
