import globals as globals,os,requests,base64
from azw.kv import *

#old method, only used for testing
def get_bearer_token():
    formatted_string = globals.conf_dict['client']+':'+globals.secret
    auth = base64.b64encode(formatted_string.encode('ascii')).decode('ascii')
    headers =   {'Accept':'application/json', 'Authorization':'Basic ' + auth, 'Content-Type':'application/x-www-form-urlencoded', 'cache-control':'no-cache'}
    params = 'grant_type=client_credentials&scope=system%2FPatient.read%20system%2FObservation.read%20system%2FDiagnosticReport.read%20system%2FCondition.read%20system%2FEncounter.read%20system%2FMedicationRequest.read'

    r = requests.post(globals.conf_dict['auth_url'], headers=headers,data=params) 

    bearer=r.json()['access_token']
    return bearer


def set_bearer_token():
    formatted_string = globals.conf_dict['client']+':'+globals.secret
    auth = base64.b64encode(formatted_string.encode('ascii')).decode('ascii')
    headers =   {'Accept':'application/json', 'Authorization':'Basic ' + auth, 'Content-Type':'application/x-www-form-urlencoded', 'cache-control':'no-cache'}
    params = 'grant_type=client_credentials&scope=system%2FPatient.read%20system%2FObservation.read%20system%2FDiagnosticReport.read%20system%2FCondition.read%20system%2FEncounter.read%20system%2FMedicationRequest.read'

    r = requests.post(globals.conf_dict['auth_url'], headers=headers,data=params) 

    globals.bearer_token=r.json()['access_token']


##old method
def make_request(bearer, resource, idstring):
    headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir',
               'Authorization': 'Bearer ' + bearer}

    r = requests.get(
        globals.conf_dict['url'] + resource + '?' + idstring,
        headers=headers)
    return r

def make_request_global(resource, idstring):
    if globals.bearer_token == None:
        set_bearer_token()
    headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir',
               'Authorization': 'Bearer ' + globals.bearer_token}

    r = requests.get(
        globals.conf_dict['url'] + resource + '?' + idstring,
        headers=headers)
    if r.status_code==401:
        set_bearer_token()
        headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir',
               'Authorization': 'Bearer ' + globals.bearer_token}
        r = requests.get(globals.conf_dict['url'] + resource + '?' + idstring, headers=headers) #will this work?
    return r

'''
# Essential method for making requests
'''
def make_hapi_request(resource, idstring):
    headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir'}

    r = requests.get(
        URL + resource + '?' + idstring,
        headers=headers)
    return r

def get_reference(bearer,reference):
    headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir',
               'Authorization': 'Bearer ' + bearer}

    r = requests.get(
        globals.conf_dict['url'] + reference,
        headers=headers)
    return r

def get_pid(bearer, cmrn):
    try:
        return \
        make_request(bearer, 'Patient', 'identifier=urn:oid:2.16.840.1.113883.3.1662.100|' + cmrn).json()['entry'][0][
            'resource']['id']
    except:
        print("no matches for CMRN")

def get_pid_global(cmrn):
    if globals.bearer_token == None:
        set_bearer_token()
    try:

        #need exception hadnling here
        return \
        make_request_global('Patient', 'identifier=urn:oid:2.16.840.1.113883.3.1662.100|' + cmrn)
    except:
        print("no matches for CMRN")

def get_pt_from_pid(cmrn):
    if globals.bearer_token == None:
        set_bearer_token()
    try:
        return \
        make_request_global('Patient', 'identifier=urn:oid:2.16.840.1.113883.3.1662.100|' + cmrn)
    except:
        print("no matches for CMRN")

def get_next_page(urlstring):
    if globals.bearer_token == None:
        set_bearer_token()
    headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir',
               'Authorization': 'Bearer ' + globals.bearer_token}

    r = requests.get(urlstring, headers=headers)
    if r.status_code==401:
        set_bearer_token()
        headers = {'Accept': 'application/json+fhir', 'Content-Type': 'application/json+fhir',
               'Authorization': 'Bearer ' + globals.bearer_token}
        r = requests.get(urlstring, headers=headers)
    return r

#print(get_bearer_token())

