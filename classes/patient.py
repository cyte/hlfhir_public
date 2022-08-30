import pandas as pd 
import fhirclient.models.address as a

##class function is deprecated
class Patient:
	pt_json = ''
	pid = None
	cmrn = None
	name_full_formatted = None
	birthDate = None 
	gender = None
	zipCode = None
	race = None
	ethnicity = None

	def __init__(self,json):
		self.pt_json = json
		try:
			self.pid = json['id']
		except:
			pass 
		self.cmrn= get_cmrn(json)
		self.name_full_formatted = get_full_name(json)
		self.birthDate = get_birth_date(json)
		self.gender = get_gender(json)
		self.zipCode = get_zip_code(json)
		self.race = get_race(json)
		self.ethnicity = get_ethnicity(json)

def get_cmrn(pt_json):
	try:
		for i in range(0,len(pt_json['identifier'])):
			if pt_json['identifier'][i]['system'] in ['urn:oid:2.16.840.1.113883.3.787.0.0','urn:oid:2.16.840.1.113883.3.1662.100','http://hospital.smarthealthit.org']: #NOTE, 1) you have to add this for every site 2) ADDED HAPI TO TEST
				return pt_json['identifier'][i]['value']
	except:
		return 'null'

def get_full_name(pt_json):
	if 'name' in pt_json:
		first = ' '.join(pt_json['name'][0]['given']).upper()
		last =  pt_json['name'][0]['family'].upper()
		if 'suffix' in pt_json['name'][0]:
			suffix = ' ' + ' '.join(pt_json['name'][0]['suffix']).upper()
		else:
			suffix = ""
		return last + suffix + ", " + first
	else:
		return 'null'

def get_birth_date(pt_json):
	if 'birthDate' in pt_json:
		return pt_json['birthDate']
	else:
		return 'null'


def get_gender(pt_json):
	if 'gender' in pt_json:
		return pt_json['gender'].upper()
	else:
		return 'null'


def get_zip_code_old(pt_json):
	if 'address' in pt_json:
		for i in range(0,len(pt_json['address'])):
			if pt_json['address'][i]['use'] == 'home':
				if 'postalCode' in pt_json['address'][i]:
					return pt_json['address'][i]['postalCode']
	else:
		return 'null'

##
##	This method works for all FHIR data tested
##
def get_race(_json):
	raceDef = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'
	if 'extension' in _json:
		try:
			for i in _json['extension']:
				if i['url']==raceDef:
					return (', '.join(pd.json_normalize(i['extension'])['valueCoding.display'].dropna()))						
		except:
			return 'null+issue'
	else:
		return 'null'

##
##	This method works for all FHIR data tested
##
def get_ethnicity(_json):
	ethDef = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'
	if 'extension' in _json:
		try:
			for i in _json['extension']:
				if i['url']==ethDef:
					if 'valueCoding.display' in pd.json_normalize(i['extension']).columns:
						return (', '.join(pd.json_normalize(i['extension'])['valueCoding.display'].dropna()))
					elif 'valueString' in pd.json_normalize(i['extension']).columns:
						return (', '.join(pd.json_normalize(i['extension'])['valueString'].dropna()))
		except:
			return 'null+issue'
	else:
		return 'null'

##
##	This method works for all FHIR data tested
##
def get_zip_code(pt_json):
	if 'address' in pt_json:
		for i in range(0,len(pt_json['address'])):
			try:
				return a.Address(pt_json['address'][i]).postalCode 
			except:
				pass
	else:
		return 'null'

