import fhirclient.models.patient as p
import fhirclient.models.encounter as e
import fhirclient.models.condition as c 
import fhirclient.models.observation as o


##This is a class to store FHIR data with relevant methods

class FHIRData:
    '''holds data from session'''
    smart = None 
    patients=[]
    encounters=[]
    conditions=[]
    observations=[]
    def __init__(self, smart):
        self.smart = smart


    
    def pts_from_ids(self,res):
        for i in res:
            try:
                self.patients.append(p.Patient(i.result().json()['entry'][0]['resource']))
            except:
                "error"
    
    def pts_from_eids(self,res):
        for i in res:
            try:
                self.patients.append(p.Patient(i.result().json()['entry'][0]['resource']))
            except:
                "error"
    
    def enc_from_ids(self,res):
        for i in res:
            try:
                self.encounters.append(e.Encounter(i.result().json()['entry'][0]['resource']))
            except:
                "error"
    
    def dx_from_enc(self,res):
        for i in res:
            try:
                #if i.result().json()['total']>0: Doesnt work in Cerner...
                for j in range(0,len(i.result().json()['entry'])):
                    self.conditions.append(c.Condition(i.result().json()['entry'][j]['resource']))
            except:
                print("error")
    
    
    '''
    using FHIRclient
    '''
    def pts_from_concurrency(self,res):
        for i in res:
            for j in i.result():
                self.patients.append(j)

    def encs_from_concurrency(self,res):
        for i in res:
            for j in i.result():
                self.encounters.append(j)
    
    def encs_from_patients(self):
        for i in self.patients:
            try:
                search = e.Encounter.where(struct={'subject':i.id})
                for j in search.perform_resources(self.smart.server):
                    self.encounters.append(j)
                    
            except:
                pass 

    def conditions_from_patients(self):
        for i in self.patients:
            try:
                search = c.Condition.where(struct={'subject':i.id,'category':'encounter-diagnosis'})
                for j in search.perform_resources(self.smart.server):
                    self.conditions.append(j)
                    
            except:
                pass  
    
        
    def conditions_from_concurrency(self,res):
        for i in res:
            for j in i.result():
                self.conditions.append(j)
    
    
    def obs_from_concurrency(self,res):
        for i in res:
            for j in i.result():
                self.observations.append(j)
    
    def return_pids_from_enc(self):
        pids = []
        for i in self.encounters:
            pid = i.subject.reference.split('/')[1]
            if pid not in pids:
                pids.append(pid)
        return pids
    def return_enc_pid_pairs_from_enc(self):
        pair_array = []
        for i in self.encounters:
            eid = i.id
            pid = i.subject.reference.split('/')[1]
            pair_array.append([eid,pid])
        return pair_array

    '''
    prints counts
    '''
    def print_counts(self):
        print(f'Patients:\t{len(self.patients)}')
        print(f'Encounters:\t{len(self.encounters)}')
        print(f'Conditions:\t{len(self.conditions)}')
        print(f'Observations:\t{len(self.observations)}')