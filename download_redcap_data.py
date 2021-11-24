import configparser
import os

def mkdirp(newpath):
    if not os.path.exists(newpath):
        os.makedirs(newpath)

def make_redcap_api_call(redcap_api_url, data, logging, post):

    try:
        log_error_str = """
            redcap rest call was unsuccessful
            or target server is down/ check configuration
            %s
            """ % (data)
        response = post(redcap_api_url, data)
        if response.status_code == 200:
            return response.content
        else:
            logging.error('%s : status_code: %s' %
                          (log_error_str, response.status_code))

    except Exception as e:
        logging.error('log_error_str : %s' % (e))


def read_config(config_file, logging, Path):

    config = configparser.ConfigParser()
    config.optionxform = str
    config.readfp(Path(config_file).open(), str(config_file))

    sections = [section for section in config.sections()]
    logging.info("availabe configs: %s" % (sections))

    return config


def save_file(folder_path, file_name, data_string, join, Path, logging,
              record_id, title):
    """Save file to local or shared location

    Args:
        folder_path (string): folder_path
        file_name (string): file_name
        data_string (string): data which will be written to file
    """

    full_path = join(folder_path, file_name)
    # taking care of windows path
    full_path = full_path.replace('\\', '/')
    full_path = Path(full_path)
    full_path.write_bytes(data_string)
    logging.info("""
    Recrod_id:%s and title:%s File has been downloaded at %s
    """ % (record_id, title, full_path))


def main(config_file, pid_titles, logging, post, join, environ, Path, redcap_api_url, where_to_save):

    error_list = []
    # read config file
    config = read_config(config_file, logging, Path)

    # parse config
    # redcap_api_url = config._sections['global']['redcap_api_url']
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

        record_id = request_payload['record_id']
        title = request_payload['title']

        # creating export path and filename
        file_name = request_payload['export_filename']
        local_export_path = request_payload['local_export_path']
        shared_export_path = request_payload['export_path']

        if data_string == None:
            # API called failed
            error_list.append(record_id)
            break
        
        mkdirp(local_export_path)
        save_file(local_export_path, file_name,
                  data_string, join, Path, logging, record_id, title)

        try:

            if where_to_save == "local_and_pdrive":
                save_file(shared_export_path, file_name,
                          data_string, join, Path, logging, record_id, title)

        except FileNotFoundError as e:
            error_str = "Issue saving file to shared location: %s  and excpetion is: %s" % (
                shared_export_path, e)

            logging.error(error_str)
            error_list.append(record_id)

    if len(error_list) > 0:
        logging.error("""All files are saved local location and shared location , EXCEPT following files with following recording id:
        %s
        """ % (error_list))
        raise()


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

        logging.basicConfig(level=logging.DEBUG)

        if len(argv) != 5:
            logging.error("""Wrong format or arguments :
             please try like 'python download_recap_data.py config_file pid""")

        [config_file, pid_titles, redcap_api_url, where_to_save] = argv[1:]
        main(config_file, pid_titles, logging, post,
             join, environ, Path, redcap_api_url, where_to_save)

    _main_ocap()
