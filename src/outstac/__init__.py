import os
import sys
import json
from pystac import * #, Collection #, CatalogType #, EOItem, MediaType, EOAsset, CatalogType
#from shapely.geometry import shape
import datetime
#from .atom import Atom
#from .ops import post_atom
import hashlib
import requests
import click
import logging
#from webdav3.client import Client
import owncloud

logging.basicConfig(stream=sys.stderr, 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

template = """<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <title type="text"></title>
        <summary type="html"></summary>
        <link rel="enclosure" type="application/octet-stream" href=""/>
        <date xmlns="http://purl.org/dc/elements/1.1/"></date>
        <published></published>
        <identifier xmlns="http://purl.org/dc/elements/1.1/"></identifier>
    </entry>
    </feed>"""

def make_dir(client, path):
    
    try:
        client.file_info(path).is_dir()
    except owncloud.ResponseError as e:
        if e.status_code == 404:
            client.mkdir(path)
    

@click.command()
@click.argument('sources', nargs=-1, required=True)
@click.option('--job', 'job',  required=True, help='job identifer')
@click.option('--endpoint', 'endpoint', help='catalog endpoint')
@click.option('--username', 'username', help='catalog username')
@click.option('--apikey', 'api_key', help='catalog api key')
@click.option('--store-host', 'store_host', required=True, help='store endpoint')
@click.option('--store-username', 'store_username', required=True, help='store username')
@click.option('--store-apikey', 'store_api_key', required=True, help='store api key')
@click.option('--outputfile', 'outputfile', required=True, help='outputfile')
def main(job, sources, endpoint, username, api_key, store_host, store_username, store_api_key,outputfile):

    oc = owncloud.Client(store_host)
    
    oc.login(store_username, 
             store_api_key)

    enclosures = []
    
    for source in sources:
    
        base_path = source

        base_source = os.path.basename(source)

        stac_catalog = os.path.join(source, 'catalog.json')

        cat = Catalog.from_file(stac_catalog)

        uids = []

        for item in cat.get_items():

            logging.info(item.id)

            for index, asset in item.assets.items():

                remote_file = '/'.join([job, base_source, asset.get_absolute_href().replace(base_path + '/', '')])
                local_file = asset.get_absolute_href() #.replace(base_path, '.')

                # create folders one after the other
                for index, p in enumerate(os.path.dirname(remote_file).split('/')):

                    make_dir(oc, 
                             '/'.join(os.path.dirname(remote_file).split('/')[0:index+1]))


                # upload asset
                logging.info('Publishing {} to {}'.format(local_file, remote_file))

                oc.put_file(remote_file, 
                            local_file)


            # publish the item.json
            for link in item.get_links():

                if link.rel == 'self':

                    remote_file = '/'.join([job, base_source, link.target.replace(base_path + '/', '')])
                    local_file = link.target #.replace(base_path, '.')

                    oc.put_file(remote_file, 
                                local_file)

        # publish the catalog.json file
        remote_file = '/'.join([job, base_source, stac_catalog.replace('file://', '').replace(base_path + '/', '')])
        local_file = stac_catalog.replace('file://', '') #.replace(base_path, '.')

        oc.put_file(remote_file, 
                    local_file)

        #enclosure = '{}/remote.php/dav/files/{}/{}'.format(store_host if store_host[-1] != '/' else store_host[:-1],
        #                                                   store_username,
        #                                                   remote_file)

        
        enclosure = '/'.join([base_source, stac_catalog.replace('file://', '').replace(base_path + '/', '')])
        logging.info(enclosure)
        #logging.info(stac_catalog)
        
        #enclosures.append('/'.join([base_source, stac_catalog.replace('file://', '').replace(base_path + '/', '')]))
        enclosures.append('./{}'.format(enclosure))
     
    catalog = Catalog(id='results', description='Results')
    
    catalog.normalize_and_save(root_href='./',
                               catalog_type=CatalogType.SELF_CONTAINED)
    
    
    with open('catalog.json') as f:
        data = json.load(f)
    
    links = data['links']
    
    for enclosure in enclosures:
        
        links.append({"rel": "child", "href": enclosure})
        
    data['links'] = links
    
    
    with open('catalog.json', 'w') as json_file:
        json.dump(data, json_file)
   
    remote_file = '/'.join([job, 'catalog.json'])
    local_file = 'catalog.json'

    oc.put_file(remote_file, 
                local_file)
    
    os.remove(local_file)
    
    enclosure = '{}/remote.php/dav/files/{}/{}'.format(store_host if store_host[-1] != '/' else store_host[:-1],
                                                       store_username,
                                                       remote_file)
    
    output = {'stac:catalog': {'href': enclosure}}
    
    print(output)

    if outputfile != None:
        with open(outputfile, 'w') as outfile:
            json.dump(output, outfile)

            
if __name__ == "__main__":
    main()





