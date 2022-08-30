icd_list = ['U07.1','J40','R05','R06.02','J01.90','J11.1','J02.0','J02.9','J12.82','R50.9','J18.0','J18.9','J10.01','J10.1']
from helpers.methods import *

##class function is deprecated; kept only for methods
class Condition:
	dx_json = None
	icd_code = None
	icd_display = None
	onsetDateTime = None
	encounter_id = None
	patient_id = None

	def __init__(self,_json):
		self.dx_json = _json
		if (return_specific_icd(_json) != 0 and return_specific_icd(_json) != -1):
			icd_list = return_specific_icd(_json)
			self.icd_code=icd_list[0]
			self.icd_display=icd_list[1]
		try:
			self.onsetDateTime=_json['resource']['onsetDateTime']
		except:
			pass
		try:
			self.patient_id=_json['resource']['subject']['reference'].split('/')[1]
			self.encounter_id=_json['resource']['encounter']['reference'].split('/')[1]
		except:
			pass

def return_icd(_json):
    flattened_json = flatten_data(_json)
    try:
        icd_index = [key for key, value in flattened_json.items() if value == 'http://hl7.org/fhir/sid/icd-10-cm']
    except:
        return 0
    if len(icd_index)>0:
        index = int([i for i in icd_index[0].split('.') if i.isdigit()][0])
        return [_json['resource']['code']['coding'][index]['code'],_json['resource']['code']['coding'][index]['display']]
    else:
        return -1


def return_specific_icd(_json):
    flattened_json = flatten_data(_json)
    try:
        icd_index = [key for key, value in flattened_json.items() if value == 'http://hl7.org/fhir/sid/icd-10-cm']
    except:
        return 0

    if len(icd_index)>0:
        index = int([i for i in icd_index[0].split('.') if i.isdigit()][0])
        if _json['resource']['code']['coding'][index]['code'] in icd_list:
            return [_json['resource']['code']['coding'][index]['code'],_json['resource']['code']['coding'][index]['display']]
        else:
            return 0
    else:
        return -1

def get_dx_code(dx):
    try:
        for i in range(0,len(dx.code.coding)):
            if dx.code.coding[i].system=='http://hl7.org/fhir/sid/icd-10-cm' or dx.code.coding[i].system=='http://hl7.org/fhir/sid/icd-9-cm': #change to ICD
                return (dx.code.coding[i].code,dx.code.coding[i].display)
        return (None,None)
    except:
        return (None,None)
    