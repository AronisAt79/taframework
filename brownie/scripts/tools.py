from scripts.coordinator import fetch_coordinator_config
from scripts.prover import proof_request, queryProverTasks, flushTasks
from scripts.w3Utils import sendTx, loadContract, setupW3Provider, getScName
from scripts.circuitUtils import calcTxCosts
from pprint import pprint
import sys

def request_proof(lcl,block,
        # testenv="REPLICA",
        retry=True,
        circuit="pi",
        mock=True,
        aggregate=False,
        mock_feedback=False
        ):
    '''
    Standalone Ultility to start a proving task for a given block,
    or return the status/result of a prover task

    Takes in the block number integer, and option Retry flag as boolean

    example:

     brownie run scripts/globals.py main request_proof 1 --network zkevmchain
    '''
    testenv=lcl['env']['testEnvironment']
    mock = str(mock).lower()
    aggregate = str(aggregate).lower()
    mock_feedback = str(mock_feedback).lower()
    retry = str(retry).lower()
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"
    sourceUrl = lcl['SOURCE_URL']
    result = proof_request(proverUrl,mock,aggregate,mock_feedback,int(block),sourceUrl,retry,circuit)
    pprint(result.json())

def request_prover_tasks(lcl):
    '''
    Standalone Ultility to query prover node(s) for proof tasks status

    No input arguments

    example:

     brownie run scripts/globals.py main  queryProverTasks --network zkevmchain
    '''
    testenv=lcl['env']['testEnvironment']
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"
    result = queryProverTasks(proverUrl)
    pprint(result.json())

def flush_prover(lcl,cache,pending,completed):
    '''
    Standalone Ultility to flush prover node(s) tasks' register

    example:

    brownie run scripts/globals.py main  flush_prover --network zkevmchain
    '''
    testenv=lcl['env']['testEnvironment']
    cache=str(cache).lower()
    pending=str(pending).lower()
    completed=str(completed).lower()
    proverUrl = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+"prover"

    result = flushTasks(proverUrl,cache,pending,completed)

def get_config(lcl,node="coordinator", params=f'[]', print_result=True):
    testenv=lcl['env']['testEnvironment']
    coordinator_url = lcl['env']["rpcUrls"][f'{testenv}'"_BASE"]+f'{node}'
    result = fetch_coordinator_config(coordinator_url, params)
    if print_result:
        try:
            pprint(result.json()['result'])
        except:
            pprint(result)
    try:
        return result.json()['result']
    except:
        return result

################################################################################
# This is the correct format of the params argument within the config rpc method
#  params=f'[{{"dummy_prover":true,\
#     "mock_prover":false,\
#     "mock_prover_if_error":false,\
#     "unsafe_rpc":true,\
#     "rpc_server_nodes":"server-testnet-geth:8545",\
#     "enable_faucet":true,\
#     "listen":"[::]:8545",\
#     "l1_rpc_url":"http://l1-testnet-geth:8545/",\
#     "l1_bridge":"0x936a70c0b28532aa22240dce21f89a8399d6ac60",\
#     "aggregate_proof":false,\
#     "circuit_name": "pi",\
#     "l1_priv":"2bdd21761a483f71054e14f5b827213567971c676928d9a1808cbfa4b7501200",\
#     "l2_rpc_url":"http://leader-testnet-geth:8545/",\
#     "params_path":"/testnet/",\
#     "prover_rpcd_url":"http://prover-rpcd:8545/"\
#     }}]'
#####################################################################################

def set_config(lcl, params):
    '''
    Can be used to modify the coordinator configuration post deployment.
    input: a string of the form "a valueOf(a) b valueOf(b) ....", for example:
    "aggregate true dummy_prover true mock false circuit_name super".
    NOTE: a, b, c etc must be keys belonging to the struct returned by get_config
    '''
    params_dict = get_config(lcl,print_result=False)
    #Create a list with user inputs and validate 
    p=params.split()
    if len(p)%2 !=0:
        print("Error: Number of inputs must be even")
    else:
        even_indexes = [i for i in range(len(p)) if i%2 == 0]
        # check if provided fields belong to the config struct:
        fields_l = list(params_dict.keys())
        fields_s = set(fields_l)
        new_fields_l = [p[i] for i in even_indexes]
        #Determin what config fields should be changed and make sure they re part of the config struct
        new_fields_s = set(new_fields_l)

        diff = new_fields_s.difference(fields_s)
        if len(diff) != 0:
            print(f"Error: Provided inputs {[i for i in list(diff)]} are not config struct members. Exiting.")
        else:
            #Replace new values
            for index in even_indexes:
                print(f'{p[index]} : {params_dict[p[index]]} >> {p[index+1]}')
                params_dict[p[index]] = p[index+1]
                # print(f'{p[index]}:{p[index+1]}')
        
        del params_dict["params_path"]
        #Create a list from resulting dictionary and format
        params_list = ["[{"]
        for param in params_dict.keys():
            if params_dict[param] in [True, False,'true', 'false']:
                # element = '"'+param+'"'+":"+str(params_dict[param]).lower().rstrip()
                element = f'"{param}":{str(params_dict[param]).lower().rstrip()}'
            else:
                # element = '"'+param+'"'+":"+'"'+params_dict[param]+'"'
                element = f'"{param}":"{params_dict[param]}"'

            params_list.append(element)
        params_list.append("}]")

        try:
            new_params = ", ".join(params_list).replace(",","",1)
            new_params_rev = new_params[::-1]
            new_params_rev = new_params_rev.replace(",","",1)
            new_params = new_params_rev[::-1]
        except Exception as e:
            print(e)
        #Invoke the config method with new configuration parameters
        get_config(lcl,params=new_params,print_result=False)

def sendTransaction(lcl, layer=2):
    pass