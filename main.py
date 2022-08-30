import argparse,classes.fhirdata as fhirdata,requests,base64,sys,io,random,time,configparser,concurrent
import pandas_gbq

from globals import *
from helpers.methods import *
from helpers.connections import *
from classes.patient import *
from classes.condition import *
from classes.encounter import *
from crypt.crypt import *
from azw.kv import *
from classes.fhirdata import *
import fhirclient.models.patient as p
import fhirclient.models.encounter as e
import fhirclient.models.condition as c 
import fhirclient.models.observation as o


def read_ini(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        for key in config[section]:
            globals.conf_dict[key] = config[section][key]
 
def to_gbq(df,worker_name):
    table_id="{0}.{1}_{2}".format(dataset_id,workshop_name,worker_name)
    pandas_gbq.to_gbq(df, table_id, project_id=project_id,if_exists='replace')

##bug: occasionally causes duplications
def to_gbq_special(resource,worker_name):
    table_id="{0}.{1}_{2}".format(dataset_id,workshop_name,worker_name)
    first_df = create_hapi_dx_df(resource[0:2500])
    pandas_gbq.to_gbq(first_df, table_id, project_id=project_id,if_exists='replace')
    for i in range(0,len(resource),2500):
        temp_df = create_hapi_dx_df(resource[i:i+2500])
        pandas_gbq.to_gbq(temp_df, table_id, project_id=project_id,if_exists='append')
        print(f"{i} complete...")

###OLD METHODs####
def iterate_cmrn(filename):
    patients = []
    conditions = []
    encounters = []
    time_start = time.perf_counter()
    bearer_start = time_start
    bearer = get_bearer_token() #REMEMBER IT ONLY LASTS 10 MINUTES
    id_list = [line.rstrip() for line in open(filename,'r')] #want to close, eventually
    for i in id_list:
        time_elapsed = (time.perf_counter() - time_start)
        bearer_time_elapsed = (time.perf_counter()-bearer_start)
        print ("%s\t%5.1f secs %5.1f secs" % (i,time_elapsed,bearer_time_elapsed))
        if bearer_time_elapsed>550:
            bearer_start=time.perf_counter()
            bearer = get_bearer_token()
        pid = get_pid(bearer,i)
        #print(pid)
        pt = make_request(bearer,'Patient','_id='+pid).json()
        try:
            patients.append(Patient(pt['entry'][0]['resource']))
            dx = make_request(bearer,'Condition','patient='+pid+'&category=encounter-diagnosis&clinical-status=active').json()
            for j in range(0,len(dx['entry'])):
                cond = Condition(dx['entry'][j])
                if cond.icd_code is not None:
                    conditions.append(cond)    
                    enc = make_request(bearer,'Encounter','_id='+cond.encounter_id).json()
                    encounters.append(Encounter(enc['entry'][0]))
        except Exception as e:
            print (e)
            continue

    return patients,conditions,encounters

def encdx(pid):
    time_start = time.perf_counter()
    conditions = []
    encounters = []
    try:
        dx = make_request_global('Condition','patient='+pid+'&category=encounter-diagnosis&clinical-status=active').json()

        for j in range(0,len(dx['entry'])):
            cond = Condition(dx['entry'][j])
            if cond.icd_code is not None:
                conditions.append(cond)    
                enc = make_request_global('Encounter','_id='+cond.encounter_id).json()
                encounters.append(Encounter(enc['entry'][0])) 
    except Exception as e:
        print (e)
    time_elapsed = (time.perf_counter() - time_start) 
    print ("%5.1f secs for pid %s" % (time_elapsed,pid))
    return conditions,encounters

def concurrent_encdx_list(pid_list):
    time_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor: # optimally defined number of threads
        res = [executor.submit(encdx, pid) for pid in pid_list]
        concurrent.futures.wait(res)
    time_elapsed = (time.perf_counter() - time_start)
    
    print ("%5.1f secs" % (time_elapsed))
    return res



##### No longer needed ####
def iterate_cmrn_global(filename):
    """This is the method that iterates using global make request"""
    patients = []
    conditions = []
    encounters = []
    time_start = time.perf_counter()
    bearer_start = time_start
    id_list = [line.rstrip() for line in open(filename,'r')] #want to close, eventually
    for i in id_list:
        time_elapsed = (time.perf_counter() - time_start)
        bearer_time_elapsed = (time.perf_counter()-bearer_start)
        print ("%s\t%5.1f secs %5.1f secs " % (i,time_elapsed,bearer_time_elapsed))

    
        pt =  get_pt_from_pid(i).json()
        try:
            pat_class = Patient(pt['entry'][0]['resource'])
            patients.append(pat_class)
            dx = make_request_global('Condition','patient='+pat_class.pid+'&category=encounter-diagnosis&clinical-status=active').json()
            for j in range(0,len(dx['entry'])):
                cond = Condition(dx['entry'][j])
                if cond.icd_code is not None:
                    conditions.append(cond)    
                    enc = make_request_global('Encounter','_id='+cond.encounter_id).json()
                    encounters.append(Encounter(enc['entry'][0]))
        except Exception as e:
            print (e)
            continue

    return patients,conditions,encounters

def patient_search(start_bd,end_bd):
    """find all patients through a range of birthdates. Uses global"""
    patients = []
    time_start = time.perf_counter()
    pt = make_request_global('Patient','birthdate=ge'+start_bd+'&birthdate=le'+end_bd).json()
    if 'entry' in pt: #may not get any results, esp on B41
        for i in range(0,len(pt['entry'])):
            try:
                 patients.append(Patient(pt['entry'][i]['resource']))
            except Exception as e:
                print (e)
                continue
        if 'link' in pt:
            next_page_link = get_next_link(pt['link'])
            while next_page_link != -1:
                print(next_page_link)
                next_page = get_next_page(next_page_link).json()
                for i in range(0,len(next_page['entry'])):
                    try:
                        patients.append(Patient(pt['entry'][i]['resource']))
                    except Exception as e:
                        print (e)
                        continue
                next_page_link = get_next_link(next_page['link'])  
            
        time_elapsed = (time.perf_counter() - time_start)
        print ("%s\t%i\t:%5.1f secs \t%5.3f" % (start_bd[:10],len(patients),time_elapsed,time_elapsed/len(patients)))
    return patients

def sb_concurrent_patient_search():
    """iterates through birthdates 1 day at a time; still need some fixes but this works in B41"""
    start_day = 1
    time_start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor: # optimally defined number of threads
        res = [executor.submit(patient_search,'2000-01-0'+str(i), '2000-01-0'+str(i+1)) for i in range(start_day,9)]
        #res = [executor.submit(sb_patient_search, '1990-0'+str(i)+'-01', '1990-0'+str(i+1)+'-31') for i in range(0,8)]
        concurrent.futures.wait(res)
    time_elapsed = (time.perf_counter() - time_start)
    print ("%5.1f secs " % (time_elapsed))

    return res

###
# HAPI-Vetted Methods
###
def b41_concurrent_enc_list(eid_list):
    """Using concurrency, take a list of enc_ids and iterate over patients"""
    with concurrent.futures.ThreadPoolExecutor() as executor: # optimally defined number of threads
        res = [executor.submit(make_request_global, 'Encounter', '_id='+eid) for eid in eid_list]
        concurrent.futures.wait(res)
    return res

def b41_concurrent_enc_to_dx(pair_array):
    '''
    Takes existing FHIR data and gets conditions
    '''
    with concurrent.futures.ThreadPoolExecutor() as executor: # optimally defined number of threads
        #res= [executor.submit(make_hapi_request, 'Condition','encounter='+eid+'&category=encounter-diagnosis&clinical-status=active') for eid in eid_array]
        res= [executor.submit(make_request_global, 'Condition','patient='+pid+'&encounter='+eid) for eid,pid in pair_array]
        concurrent.futures.wait(res)
    return res

def b41_concurrent_enc_to_pts(pid_array):
    '''
    Takes existing FHIR data and gets patients
    '''
    with concurrent.futures.ThreadPoolExecutor() as executor: # optimally defined number of threads
        res= [executor.submit(make_request_global, 'Patient', '_id='+pid) for pid in pid_array]
        concurrent.futures.wait(res)
    return res


####MAIN#####
parser=argparse.ArgumentParser()
parser.add_argument("-cmrn",type=str,help='enter file of cmrns')
parser.add_argument("-b",action="store_true",help='birthdate query')
parser.add_argument("-e",type=str,help='enter file of encntr_ids to run enc-->cond/pt')
parser.add_argument("-gbq",type=str,help='worker_name')
parser.add_argument("-p",type=str,help='enter file of patient_ids to run pt-->enc-->cond-->dc')

read_ini("config.ini")
set_azure_params()
globals.secret = obtain_key(conf_dict['environment'])
args = parser.parse_args()
if args.e:
    #smart = client.FHIRClient(settings=settings)
    fdata = FHIRData('')
    #eid_list = [line.rstrip() for line in open(args.e,'r')] #original way
    set_key()
    eid_list = list(filter(None,decrypt(args.e).split('\n'))) #some have ''
    eid_data = b41_concurrent_enc_list(eid_list)
    fdata.enc_from_ids(eid_data)
    print("eid_data finished...")
    pa = fdata.return_enc_pid_pairs_from_enc()
    print("enc_pid pairs complete...")
    cond_data = b41_concurrent_enc_to_dx(pa)
    print("enc to dx complete....")
    fdata.dx_from_enc(cond_data)
    print("cond data finished...")
    pid_list=fdata.return_pids_from_enc()
    pid_data=b41_concurrent_enc_to_pts(pid_list)
    print("pid data finished...")
    fdata.pts_from_ids(pid_data)
    print("printing counts...")
    fdata.print_counts()
    
    time_start = time.perf_counter()
    if args.gbq:
        print("uploading to gbq...")
        pt_df = create_hapi_pt_df(fdata.patients)
        e_df = create_hapi_enc_df(fdata.encounters)
        #c_df = create_hapi_dx_df(fdata.conditions)
        to_gbq(pt_df,args.gbq+'_patient')
        to_gbq(e_df,args.gbq+'_encounter')
        to_gbq_special(fdata.conditions,args.gbq+'_condition')
        time_elapsed = (time.perf_counter() - time_start)
        print ("%5.1f secs " % (time_elapsed))







