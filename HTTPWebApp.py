# coding utf-8
import json
import requests

class HTTPWebApp:
    api_key  = 'AIzaSyAm3O-hhFSJ43J4fv0bCdd3ZvKxQArZdN0'
    base_url = 'https://nnct-taskfin.web.app/api/v1/'
    
    def __init__(self, email, password):
#        get idToken
#        curl 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=[API_KEY]' \
#        -H 'Content-Type: application/json' \
#        --data-binary '{'email':'[user@example.com]', 'password':'[PASSWORD]', 'returnSecureToken':true}'
        response = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(self.api_key),
                                json.dumps({'email':email,
                                            'password':password,
                                            'returnSecureToken':True}),
                                headers = {'Content-Type': 'application/json'})
#        dict_keys(['kind', 'localId', 'email', 'displayName', 'idToken', 'registered', 'refreshToken', 'expiresIn'])
        self.idToken = response.json()['idToken']
        print("init")
    
    def getToken(self):
        return self.idToken
        
    def postBodyTemperature(self, place_id, student_id, body_T):
        response = requests.post('{}body_temperatures'.format(self.base_url),
                                json.dumps({'place_id': place_id,
                                            'student_id': student_id,
                                            'body_temperature': body_T}),
                                headers = {'Content-Type': 'application/json',
                                           'Authorization': 'Bearer {}'.format(self.idToken)})
        return response.status_code
    
    def getPlaces(self):
        response = requests.get('{}places'.format(self.base_url),
                                headers = {'Authorization': 'Bearer {}'.format(self.idToken)})
        return response.json()
