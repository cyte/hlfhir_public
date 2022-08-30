
from helpers.methods import *

#class function is deprecated
class Observation:
	obs_json = None
	obs_id = None
	issued = None
	effective_DT = None
	obsType = None
	value = None
	unit = None
	encounter = None
	loinc_code = None
	#icd_code = None
	#icd_display = None
	#nsetDateTime = None
	#encounter_id = None
	#patient_id = None

	def __init__(self,_json):
		self.obs_json = _json
		try:
			self.obs_id=_json['resource']['id']
		except:
			pass

		try:
			self.issued = _json['resource']['issued']
		except:
			pass

		try:
			self.obsType = _json['resource']['code']['text']
		except:
			pass

		if 'encounter' in _json['resource']:
			self.encounter = _json['resource']['encounter']['reference']
		if 'effectiveDateTime' in _json['resource']:
			self.effective_DT = _json['resource']['effectiveDateTime']
		if 'valueQuantity' in _json['resource']:
			try:
				self.value=_json['resource']['valueQuantity']['value']
			except:
				pass
			try:
				self.unit=_json['resource']['valueQuantity']['unit']
			except:
				pass
		try:
			self.loinc_code=get_loinc(_json['resource']['code']['coding'])
		except:
			pass
		'''
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
		'''

def get_loinc(_json):
	flat_loinc = pd.json_normalize(_json)
	if flat_loinc[flat_loinc['system']=='http://loinc.org']['code'].any():
		for i in  flat_loinc[flat_loinc['system']=='http://loinc.org']['code']:
			return i
