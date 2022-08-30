import hashlib,json
from globals import *
from classes.patient import *
from classes.condition import *
import pandas as pd

##no longer used
def grouper(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def deid(string):
    ##this method is intentionally left blank; must use own DEID
    pass

def flatten_data(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def save_json(_json,filename):
        f=open(filename,'w')
        json.dump(_json,f)
        f.close()

def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    f.close()
    return data


'''
    obs_json = None
    obs_id = None
    issued = None
    effective_DT = None
    obsType = None
    value = None
    unit = None
    encounter = None
    loinc_code = None
    '''

def get_next_link(_json):
    link_path = pd.json_normalize(_json)
    if link_path[link_path['relation']=='next']['url'].any():
        for i in link_path[link_path['relation']=='next']['url']:
            return i
    return -1

###
# GBQ related functions in HAPI/B41
###
def create_hapi_pt_df(pt):
    pt_schema = {'patient_id':[],'mrn':[],'birthDate':[],'gender':[],'zipCode':[],'ethnicity':[],'race':[]}
    pt_df = pd.DataFrame(pt_schema)
    for i in range(0,len(pt)):
        zip_code = None
        try:
            zip_code = pt[i].address[0].postalCode
        except:
            zip_code = None
        pt_df = pt_df.append({'patient_id':deid(pt[i].id+'.0')
                ,'mrn':deid(get_cmrn(pt[i].as_json())+'.0') #be careful; this will change for Cerner
                ,'birthDate':pt[i].birthDate.isostring
                ,'gender':pt[i].gender
                ,'zipCode':zip_code
                ,'ethnicity':get_ethnicity(pt[i].as_json())
                ,'race':get_race(pt[i].as_json())},ignore_index=True)
    return pt_df

def create_hapi_dx_df(dx):
    dx_schema = {'patient_id':[],'encounter_id':[],'icd_code':[],'icd_display':[],'onsetDateTime':[]}
    dx_df = pd.DataFrame(dx_schema)
    for i in range(0,len(dx)):
        #make this more pythonic; ALSO REMEMBER IT IS SNOMED CURRENTLY BC OF HAPI
        #consider updt_dt_tm and recorded dt
        #consider category
        dx_pair = get_dx_code(dx[i])
        dx_onsetDtTm = None
        try:
            dx_onsetDtTm = dx[i].onsetDateTime.isostring
        except:
            dx_onsetDtTm = None
        dx_df = dx_df.append({'patient_id':deid(dx[i].subject.reference.split('/')[1]+'.0')
            ,'encounter_id':deid(dx[i].encounter.reference.split('/')[1]+'.0')
            ,'icd_code':dx_pair[0]
            ,'icd_display':dx_pair[1]
            ,'onsetDateTime':dx_onsetDtTm}
            ,ignore_index=True)
    return dx_df

def create_hapi_enc_df(enc):
    e_schema = {'encounter_id':[],'patient_id':[],'enc_type_cd':[],'enc_type_disp':[],'start_dt':[],'end_dt':[]}
    e_df = pd.DataFrame(e_schema)
    for i in range(0,len(enc)):
        enc_end_dt = None
        try:
            enc_end_dt = enc[i].period.end.isostring
        except:
            enc_end_dt = None
        e_df = e_df.append({'encounter_id':deid(enc[i].id+'.0')
            ,'patient_id':deid(enc[i].subject.reference.split('/')[1]+'.0')
            ,'enc_type_cd':enc[i].class_fhir.code
            ,'enc_type_disp':enc[i].class_fhir.display
            ,'start_dt':enc[i].period.start.isostring
            ,'end_dt':enc_end_dt}
            ,ignore_index=True)
    return e_df

def create_hapi_obs_df(obs):
    obs_schema = {'obs_id':[],'encounter_id':[],'issued':[],'effective_dt_tm':[],'obsType':[],'value':[],'unit':[],'loinc_code':[]}
    obs_df = pd.DataFrame(obs_schema)
    for i in range(0,len(obs)):
        #need to make this more python
        #note that valuestring & valuedate null for HAPI; MAY NOT be for CERNER
        o_value = None
        o_unit = None
        if obs[i].valueQuantity!=None:
            o_value=obs[i].valueQuantity.value
            o_unit=obs[i].valueQuantity.unit
        elif obs[i].valueCodeableConcept!=None:
            o_value=obs[i].valueCodeableConcept.coding[0].display #this may not work
        obs_df = obs_df.append({'obs_id':deid(obs[i].id)
            ,'encounter_id':obs[i].encounter.reference.split('/')[1] #need to fix this
            ,'issued':obs[i].issued.isostring
            ,'effective_dt_tm':obs[i].effectiveDateTime.isostring
            ,'obsType':obs[i].code.text
            ,'value':o_value
            ,'unit':o_unit
            ,'loinc_code':get_loinc(obs[i].as_json()['code']['coding'])}
            ,ignore_index=True)
    return obs_df


