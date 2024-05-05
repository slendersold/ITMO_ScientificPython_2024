import requests
import re
import json
from Bio import SeqIO
import subprocess
import sys
class BioPythonLib:
    def __init__(self, file_name):
        self.regex = {"Protein": "^.*([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}).*$",
                      "DNA": "^.*(ENS[A-Z]{0,4}|MGP_[A-Za-z0-9]{0,10}_)(E|FM|G|GT|P|R|T)(\d{11}).*$"}
        self.filename = file_name
        self.SeqIO_ids = []
        self.output = {"seqkit_result": self.seqkit_stats()}
        self.biopython_parser()
        self.access_database()
        self.show_output(self.output)

    def seqkit_stats(self):
        seqkit = subprocess.run(("seqkit", "stats", self.filename, "-a"),
                                capture_output=True,
                                text=True)

        # If error arises
        if (seqkit.stderr != ''):
            print("Error:", seqkit.stderr)
            sys.exit(1)

        # Output
        if (seqkit.stdout == ''):
            print("Output is empty. Check the fasta file")
            sys.exit(1)

        seqkit_out = seqkit.stdout.strip().split('\n')

        # split names and values
        prop_names = seqkit_out[0].split()[1:]
        prop_vals = seqkit_out[1].split()[1:]

        seq_result = dict(zip(prop_names, prop_vals))
        # using zip
        self.seqkit_result = {"fasta_seqkit_stat_info": seq_result,
                              "fasta_type": seq_result['type'],
                              "fasta_num_seqs": int(seq_result['num_seqs']),
                              }

        return self.seqkit_result

    def biopython_parser(self):
        sequences = SeqIO.parse(self.filename, 'fasta')  # seq input; returns an iterator
        regex = self.regex[self.seqkit_result["fasta_type"]]

        for seq in sequences:

            seq_description = seq.description
            seq_sequence = seq.seq

            # seq_id
            match = re.fullmatch(regex, seq_description)

            if match:
                if self.seqkit_result["fasta_type"] == 'DNA':
                    id_chunks = re.findall(regex, seq_description)
                    seq_id = [''.join(chunk) for chunk in id_chunks][0]

                if self.seqkit_result["fasta_type"] == 'Protein':
                    seq_id = re.findall(regex, seq_description)[0][0]

                self.SeqIO_ids.append(seq_id)
                self.output[f'seq_id_{seq_id}_info'] = {"description": seq_description, "sequence": seq_sequence}

            else:
                print("No ID match found.")
                sys.exit(1)

    def get_uniprot(self, ids: list):
        accessions = ','.join(ids)
        endpoint = "https://rest.uniprot.org/uniprotkb/accessions"
        http_function = requests.get
        http_args = {'params': {'accessions': accessions}}

        return http_function(endpoint, **http_args)

    def get_ensembl(self, ids: list):
        server = "https://rest.ensembl.org"
        ext = "/lookup/id"
        headers = {"Content-Type": "application/json"}
        x = {"ids": ids}
        y = json.dumps(x)
        resp = requests.post(server + ext, headers=headers, data=y)
        return resp

    def parse_response_uniprot(self, resp: dict):
        resp = resp.json()
        resp = resp["results"]
        output = {}
        for val in resp:
            acc = val['primaryAccession']
            species = val['organism']['scientificName']
            gene = val['genes']
            seq = val['sequence']
            output[acc] = {'organism': species, 'geneInfo': gene, 'sequenceInfo': seq, 'type': 'protein'}

        return output

    def parse_response_ensembl(self, resp: dict):
        resp = resp.json()
        output = {}
        for val in resp.values():
            id = val['id']
            species = val['species']
            gene = {
                'assembly_name': val['assembly_name'],
                'biotype': val['biotype'],
                'canonical_transcript': val['canonical_transcript']
            }
            seq = {
                'seq_region_name': val['seq_region_name'],
                'start': val['start'],
                'end': val['end']
            }
            object_type = val['object_type']
            output[id] = {'organism': species,
                          'geneInfo': gene,
                          'sequenceInfo': seq,
                          'type': object_type}

        return output

    def access_database(self):
        ids = self.SeqIO_ids
        if self.seqkit_result["fasta_type"] == 'Protein':
            data = self.parse_response_uniprot(self.get_uniprot(ids))
            self.output["DB_name"] = "uniprot"
            self.output["DB_result"] = data
        elif self.seqkit_result["fasta_type"] == 'DNA':
            data = self.parse_response_ensembl(self.get_ensembl(ids))
            self.output["DB_name"] = "ENSEMBL"
            self.output["DB_result"] = data

    def show_output(self, v, indent=0):
        for key, value in v.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                self.show_output(value, indent + 1)
            else:
                print('\t' * (indent + 1) + str(value))