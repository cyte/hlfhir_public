##class is no longer needed
class Encounter:
	enc_json = None
	start_dt = None
	end_dt = None
	FIN = None 										#wip
	encclass = None
	encounter_id = None
	patient_id = None 
	reasonCode = None  							#WIP; what if more?
	serviceType = None

	def __init__(self,_json):
		self.enc_json = _json
		self.encounter_id = _json['resource']['id']
		if 'period' in _json['resource']:
			self.start_dt = _json['resource']['period']['start']
			if 'end' in _json['resource']['period'].keys():
				self.end_dt = _json['resource']['period']['end']
		try:
			self.encclass = _json['resource']['class']['display']
			self.patient_id=_json['resource']['subject']['reference'].split('/')[1]
			self.reasonCode = _json['resource']['reasonCode'][0]['text']
		except:
			pass
