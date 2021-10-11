import configparser
import subprocess

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
def shared_location_upload(logging, request_payload, data_string ):
    p_drive_access_user = os.environ.get('jnk_user')
    p_drive_access_pass = os.environ.get('jnk_pass')
    subprocess.check_call(['sudo', 'mount','-t', 'cifs', '//kumc-data01/protected/', '/mnt/kumc-data01/protected/', '-o' , 'user=ADC_Exports' , ',domain=kumc',',password=*Ng3QYam', '||', 'true'])
    
    # creating export path and filename
    export_filename = request_payload['export_filename']
    export_path = request_payload['export_path']
    full_path = join(export_path, export_filename)
    local_store_jnk = './export'
    local_path = os.path.join(local_store_jnk, export_filename)

    # exporting to file
    full_path = Path(full_path)
    try:
        full_path.write_bytes(data_string)
        logging.info("File has been downloaded at P_drive at: %s ." % (full_path))
    except Exception as e:
        logging.error("""
            The error reported while placing the file in P Drive was:
            %s
            """ % (e))
    local_path = Path(local_path)
    local_path.write_bytes(data_string)
    logging.info("File has been downloaded at local loc ./export %s ." % (local_path))

    subprocess.check_call(['sudo', 'umount', '-f', '//mnt/kumc-data01/protected/', '||', 'true'])

    logging.info("File has been downloaded at %s ." % (full_path))


def main(config_file, pid_titles, logging, post, join, environ, Path, redcap_api_url):
    # read config file
    config = read_config(config_file, logging, Path)

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


        shared_location_upload(logging, request_payload, data_string )

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
