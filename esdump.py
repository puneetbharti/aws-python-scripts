import os
import subprocess
import requests


config = {
    "input":{
        "host":"localhost",
        "port":"9200",
        "index":"elasticlogs"
     },
    "output":{
        "host":"localhost",
        "port":"9200",
        "index":"bbm",

    }
}

url = "http://%s:%s" % (config['input']['host'], config['input']['port'])
output_url = "http://%s:%s" % (config['output']['host'], config['output']['port'])

def exec_esdump():
    ed_input = "--input=%s/%s" % (url, config['input']['index'])
    ed_output = "--output=%s/%s" % (url, config['output']['index'])
    subprocess.call(["elasticdump", ed_input, ed_output, "--type=data"])
    return 0

def check_es_input():
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print("Error hitting ElasticSearch on %s, response code was %i" % (url, r.status_code))
            exit(1)
        else:
            print("Verified ElasticSearch server")
    except:
        print("Unable to hit ElasticSearch on %s" % url)
        exit(1)

def check_index_exist():
    try:
        r = requests.get("%s/%s/_settings" % (url, config['input']['index']))
        if r.status_code != 200:
            print("Unable to get settings for index '%s', error code: %i" % (config.input.index, r.status_code))
            exit(1)
    except:
        print("Unable to get ElasticSearch index on %s" % url)
        exit(1)


if __name__ == '__main__':
    check_es_input()
    check_index_exist()
    exec_esdump()