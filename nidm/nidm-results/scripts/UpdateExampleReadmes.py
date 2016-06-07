# For each document in the NIDM repository, this script checks if there is a
# public document with the same content (from title) in the Prov Store
# (https://provenance.ecs.soton.ac.uk/store). If there is none, the document is
# uploaded and its README file is updated to link to the json, turtle, svg, PDF
# and png serialisations.

# To use this script you need to have an account on the Prov Store (cf.
# https://provenance.ecs.soton.ac.uk/store/account/signup/) and to
# create a file named store_login_key.txt in the same directory including the
# following text: "mylogin:mykey" where mylogin must be replaced by your Prov
# Store login and mykey by your ApiKey (cf.
# https://provenance.ecs.soton.ac.uk/store/account/developer/)

import urllib2
import json
import logging
import os
from rdflib.compare import *
import sys
# from subprocess import call

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
NIDMRESULTSPATH = os.path.dirname(SCRIPT_PATH)

# Append test directory to path
sys.path.append(os.path.join(SCRIPT_PATH, "..", "test"))
from nidmresults.test.test_commons import *

logging.basicConfig(filename='debug.log', level=logging.DEBUG, filemode='w')
logger = logging.getLogger(__name__)


# Define title for all examples
doc_titles = dict()
doc_titles[os.path.join(
    'spm', 'example001', 'example001_spm_results.ttl')] = "SPM example 001"
doc_titles[os.path.join(
    'fsl', 'example001', 'fsl_nidm.ttl')] = "FSL example 001"
doc_titles[os.path.join(
    'spm', 'spm_results.ttl')] = "SPM"
doc_titles[os.path.join(
    'spm', 'example002', 'spm_results_2contrasts.ttl')] = "SPM example 002"
doc_titles[os.path.join(
    'spm', 'example003', 'spm_results_conjunction.ttl')] = \
    "SPM example 003: Conjunction"
doc_titles[os.path.join(
    'spm', 'example004', 'spm_inference_activities.ttl')] = \
    "SPM example 004: Inference"
doc_titles[os.path.join('fsl', 'fsl_results.ttl')] = "FSL"


def get_doc_from_title(doc_title):
    """ Find document with same title in the prov store and return URI"""
    doc_url = None

    # Retreive most recent document with same title
    url = "https://provenance.ecs.soton.ac.uk/store/api/v0/documents/" + \
          "?document_name__startswith=" + \
          doc_title + "&document_name__endswith=" + doc_title + \
          "&format=json&order_by=-created_at&limit=1"
    req = urllib2.Request(url)

    response = urllib2.urlopen(req)
    data = json.load(response)
    if data['meta']['total_count'] == 0:
        logger.debug('No document entitled: "'+doc_title+'"')
    else:
        doc_url = "https://provenance.ecs.soton.ac.uk" + \
                  data['objects'][0]['resource_uri']
        logger.info('\tLast version of this document in the ProvStore: ' +
                    '"' + doc_url + '"')
    return doc_url


# Update Readme
def write_readme(readme_file, doc_url):
    folder = os.path.dirname(readme_file)
    if not os.path.isdir(folder):
        os.mkdir(folder)

    readme_file_open = open(readme_file, 'w+')

    doc_url = doc_url.replace("api/v0/", "")

    readme_file_open.write("""
Prov store: """+doc_url+"""

Alternative serialisations: [json](""" + doc_url[:-1] +
                           """.json), [turtle](""" + doc_url[:-1] + """.ttl),
Graph: [svg](""" + doc_url[:-1] + """.svg), [PDF](""" + doc_url[:-1] +
                           """.pdf), [png](""" + doc_url[:-1] + """.png)

![Prov Graph]("""+doc_url[:-1]+""".png)

        """)
    readme_file_open.close()


def create_document(doc_json_url, doc_title):
    """ Create a new document on the ProvStore"""

    # Read json version of current document
    response = urllib2.urlopen(doc_json_url)
    # doc_json_url = response.geturl()
    doc_json = response.read()

    # Retreive ApiKey
    api_key_file = os.path.join(SCRIPT_PATH, "store_login_key.txt")
    if not os.path.isfile(api_key_file):
        logger.debug('Missing key file: ' + api_key_file)
        raise Exception(
            "No Api Key. Please specify your ApiKey in store_login_key.txt.")
    api_key_file = open(api_key_file, 'r')
    api_key = api_key_file.read()

    # Create new document on the prov store
    url = "https://provenance.ecs.soton.ac.uk/store/api/v0/documents/"
    headers = {'Content-type': "application/json",
               'Authorization': 'ApiKey '+api_key,
               'Accept': "application/json"}
    # This is a trick to avoid issue with xsd namespace
    doc_json = doc_json.replace("http://www.w3.org/2001/XMLSchema",
                                "http://www.w3.org/2001/XMLSchema#")
    data = ' {"content":'+doc_json+',"public":true,"rec_id":"'+doc_title+'"} '

    req = urllib2.Request(url, data, headers)

    response = urllib2.urlopen(req)
    data = json.load(response)

    doc_url = "https://provenance.ecs.soton.ac.uk"+data['resource_uri']
    logger.info('\tCreated document "'+doc_title+'" at: '+doc_url)

    return doc_url


def main():
    for example_file in example_filenames:
        logger.debug(" "+example_file)

        # Get title for current document
        if example_file not in doc_titles:
            doc_title = "<Title not found>"
            logger.debug('No title for document: '+example_file)
        else:
            doc_title = doc_titles[example_file]

        doc_title = "NIDM-Results: "+doc_title
        logger.info('Document entitled: '+'"'+doc_title+'"')

        doc_ttl_file = os.path.join(NIDMRESULTSPATH, example_file)

        # No more provn serialisation
        # # Update provn file from ttl
        # doc_ttl_file = doc_provn_file.replace(".provn", ".ttl")
        # call("provconvert -infile "+doc_ttl_file+" -outfile "+doc_provn_file,
        #      shell=True)

        # Compare current document with prov store
        if os.path.isfile(doc_ttl_file):
            doc_ttl_file_open = open(doc_ttl_file, 'r')
            doc_ttl = doc_ttl_file_open.read()
            doc_ttl_file_open.close()

            # Find corresponding document on the ProvStore by looking at README
            # Read README
            readme_file = os.path.join(NIDMRESULTSPATH,
                                       os.path.dirname(example_file),
                                       'README.md')
            if os.path.isfile(readme_file):
                readme_fid = open(readme_file)
                readme_txt = readme_fid.read()
                readme_fid.close()

                provstore_url_index = re.search(
                    "https://provenance.ecs.soton.ac.uk/store/" +
                    "documents/[^/]*/",
                    readme_txt)
                # Get corresponding turtle on Prov Store
                if provstore_url_index:
                    same_doc_url = readme_txt[
                        provstore_url_index.start():provstore_url_index.end()]
                else:
                    same_doc_url = None

                if same_doc_url:
                    same_doc_ttl_url = same_doc_url[:-1]+".ttl"
                    found_difference = compare_ttl_documents(doc_ttl_file,
                                                             same_doc_ttl_url)

                    if found_difference:
                        logger.info('\tDifferent from last version.')
                    else:
                        logger.info('\tSame as last version.')
                else:
                    logger.info('\tNo previous version.')
                    found_difference = True
            else:
                logger.info('\tNo README.')
                found_difference = True
        else:
            logger.info('\tNo ttl file.')
            found_difference = True

        if found_difference:
            # Convert ttl to json using Prov Translator APIs
            # FIXME: Do we still need this conversion now that we are starting
            # from ttl not provn?
            url = "https://provenance.ecs.soton.ac.uk/validator/" + \
                  "provapi/documents/"
            headers = {'Content-type': "text/turtle",
                       'Accept': "application/json"}
            req = urllib2.Request(url, doc_ttl, headers)

            response = urllib2.urlopen(req)
            doc_json_url = response.geturl()
            logger.info('\tDocument in json: '+'"'+doc_json_url+'"')
            doc_url = create_document(doc_json_url, doc_title)
        else:
            doc_url = same_doc_url

        readme_file = os.path.join(os.path.dirname(
            os.path.join(NIDMRESULTSPATH, example_file)), 'README.md')
        write_readme(readme_file, doc_url)

if __name__ == '__main__':
    main()
