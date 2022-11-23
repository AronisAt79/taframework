from scripts.rpcUtils import rpcCall
from pprint import pprint

def proof_request(proverUrl,mock,aggregate,mock_feedback,block,sourceURL,retry=False,circuit="pi"):
    '''
    Sends a proof_request for selected block, Set the retry boolean to false if: you just need the proof status
    or to invoke a new proof generation without the option to retry in case of failure
    '''

    data = f'{{"jsonrpc":"2.0", "method":"proof", "params":[{{"block":{block},"circuit":"{circuit}","aggregate":{aggregate},"mock":{mock},"mock_feedback":{mock_feedback},"rpc":"{sourceURL}", "retry":{retry}}}], "id":{block}}}'
    pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

def queryProverTasks(proverUrl, id=1):
    data=f'{{"jsonrpc":"2.0", "method":"info", "params":[], "id":{id}}}'
    # pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

def flushTasks(proverUrl,cache,pending,completed, id=1):
    cache=str(cache).lower()
    pending=str(cache).lower()
    completed=str(cache).lower()
    data = f'{{"jsonrpc":"2.0", "method":"flush", "params":[{{"cache":{cache},"pending":{pending}, "completed":{completed}}}],"id":{id}}}'
    pprint(data)
    url=proverUrl
    response = rpcCall(url,data)
    return response

