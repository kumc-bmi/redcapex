import configparser
import subprocess
import sys
import os
import pathlib2
from subprocess_calls_pdrive import Subprocess_calls_pdrive
import shutil

# Function to collect Data from REDCap using request package:
def make_redcap_api_call(redcap_api_url, data, logging, post):
    try:
        response = post(redcap_api_url, data)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception('%s - %s' %
                            (response.status_code, response.content))

    except Exception as e:
        logging.error("""
            redcap rest call was unsuccessful
            or target server is down/ check configuration
            %s
            """ % (e))

#Function to read the config fiel in the ./.env location to have the parameters for exporting files
def read_config(config_file, logging, Path):

    config = configparser.ConfigParser()
    config.optionxform = str
    config.readfp(Path(config_file).open(), str(config_file))

    sections = [section for section in config.sections()]
    logging.info("availabe configs: %s" % (sections))

    return config

# Function to place file in the P Drive:
def shared_location_upload(pid_title, logging, request_payload, data_string, subprs1):
    Config_REDCap_proj_id_carrier = os.environ.get('Config_REDCap_Project_ID')
    where_to_save_carrier = os.environ.get('where_to_save')

    # Writing files to the local location:
    local_store_jnk = './export'
    export_filename = request_payload['export_filename']
    local_path = os.path.join(local_store_jnk, export_filename)
    local_path_1 = pathlib2.Path(local_path)
    local_path_1.write_bytes(data_string)
    logging.info("File has been downloaded at local loc ./export %s ." % (local_path))

    if where_to_save_carrier == 'local_and_pdrive' or pid_title == Config_REDCap_proj_id_carrier:
        # creating export path and filename and exporting to file

        
        # testing for project not in the config project:
        if pid_title == Config_REDCap_proj_id_carrier:
            print("entered config_proj")
            export_path = request_payload['export_path']
            export_path = export_path.replace('\\', '/')
            full_path = pathlib2.Path(export_path)
            if export_path in ['./.env/redcap_projects_exports.csv', local_path]:  
                try:
                    full_path.write_bytes(data_string)
                    logging.info("File has been downloaded at P_drive at: %s ." % (full_path))
                except Exception as e:
                    logging.error("""
                        The error reported while placing the file in P Drive was:
                        %s
                        """ % (e))
        else:
            print("entered the non config_proj")
            export_path = request_payload['export_path']
            export_path = export_path.replace('\\', '/')
            export_path_comp_list = export_path.split('/')
            export_path_comp_list.remove(request_payload['export_filename'])
            export_path_1 = '/'.join(export_path_comp_list)
            full_path = pathlib2.Path(export_path_1)
            try:
                ### full_path.write_bytes(data_string)
                subprs1.copy_file_pdrive(logging, local_path_1, os.environ.get('p_Drive_mount_sable'))
                logging.info("File has been downloaded at P_drive at: %s ." % (full_path))
            except Exception as e:
                logging.error("""
                    The error reported while placing the file in P Drive was:
                    %s
                    """ % (e))

    logging.info("File has been downloaded successfull")

def main(config_file, pid_titles, logging, post, join, environ, Path, redcap_api_url):
    # read config file
    config = read_config(config_file, logging, Path)

    jnk_user_carrier = os.environ.get('jnk_user')
    jnk_pass_carrier = os.environ.get('jnk_pass')
    
    subprs1 = Subprocess_calls_pdrive()
    subprs1.mount_Pdrive_sable(jnk_user_carrier, jnk_pass_carrier, logging)

    # parse config
    #redcap_api_url = config._sections['global']['redcap_api_url']
    if pid_titles == 'ALL':
        pid_titles = [section for section in config.sections()]
    else:
        pid_titles = [pid_titles]

    for pid_title in pid_titles:
        request_payload = dict(config.items(pid_title))

        # reading key from environment variable and replace string with key
        # request_payload['token'] = environ[request_payload['token']]

        # send request to redcap
        data_string = make_redcap_api_call(
            redcap_api_url, request_payload, logging, post)

        shared_location_upload(pid_title, logging, request_payload, data_string, subprs1)

    subprs1.unmount_PDrive_sable(logging)


if __name__ == "__main__":

    def _main_ocap():
        '''
        # https://www.madmode.com/2019/python-eng.html
        '''

        import logging
        from requests import post
        from os import environ
        from os.path import join
        from sys import argv
        from pathlib2 import Path
        from dotenv import load_dotenv

        sys.path.append('../')
        load_dotenv()

        logging.basicConfig(level=logging.DEBUG)

        if len(argv) != 4:
            logging.error("""Wrong format or arguments :
             please try like 'python download_recap_data.py config_file pid""")

        [config_file, pid_titles, redcap_api_url] = argv[1:]
        main(config_file, pid_titles, logging, post,
             join, environ, Path, redcap_api_url)

    _main_ocap()
