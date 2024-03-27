import requests
import re
import json

def get_uniprot(ids: list):
    accessions = ','.join(ids)
    endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
    http_function = requests.get
    http_args = {'params': {'accessions': accessions}}
    return http_function(endpoint, **http_args)

def parse_response_uniprot(resp: dict):
    resp = resp.json()
    resp = resp["results"]
    output = {}
    for val in resp:
        acc = val['primaryAccession']
        species = val['organism']['scientificName']
        gene = val['genes']
        seq = val['sequence']
        output[acc] = {'organism':species, 'geneInfo':gene, 'sequenceInfo':seq, 'type':'protein'}

    return output

def get_ensembl(ids: list):
    server = "https://rest.ensembl.org"
    ext = "/lookup/id"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    x = {"ids": ids}
    y = json.dumps(x)
    resp = requests.post(server + ext, headers=headers, data = y)
    return resp

def parse_response_ensembl(resp: dict):
    resp = resp.json()
    output = {}
    for val in resp.values():
        id = val['id']
        species = val['species']
        gene = {
            'assembly_name':val['assembly_name'],
            'biotype':val['biotype'],
            'canonical_transcript':val['canonical_transcript']
        }
        seq = {
            'seq_region_name':val['seq_region_name'],
            'start':val['start'],
            'end':val['end']
        }
        object_type = val['object_type']
        output[id] = {'organism': species,
                       'geneInfo': gene,
                       'sequenceInfo': seq,
                       'type': object_type}

    return output

def access_database(ids: list):
    dbRegEx = {"uniprot":"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}",
               "ensembl":"ENS[A-Z]*(E|FM|G|GT|P|R|T)[0-9]{11}|MGP_[A-Za-z0-9]*_[0-9]{11}"}
    if re.fullmatch(dbRegEx["uniprot"], ids[0])!=None:
        return parse_response_uniprot(get_uniprot(ids))
    else:
        if re.fullmatch(dbRegEx["ensembl"], ids[0])!=None:
            return parse_response_ensembl(get_ensembl(ids))

# if __name__ == "__main__":
#     ids = ["ENSMUSG00000041147", "ENSG00000139618"]
#     # ids = ['P11473', 'P13053']
#     print(access_database(ids))