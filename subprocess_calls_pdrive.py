import os
import subprocess

class Subprocess_calls_pdrive:
    def __init__(self):
        ''' Constructor for this class. '''
        # Creating some member variables
        self.p_Drive_path = os.environ.get('p_Drive_path')
        self.p_Drive_mount_sable = os.environ.get('p_Drive_mount_sable')
        self.p_Drive_domain = os.environ.get('p_Drive_domain')

    def mount_Pdrive_sable(self, jnk_user, jnk_pass, logging):
        try:
            subprocess.check_call('sudo mount -t cifs %s %s -o user=%s,domain=%s,password=%s'%(self.p_Drive_path, self.p_Drive_mount_sable, jnk_user, self.p_Drive_domain, jnk_pass), shell=True)
        except Exception as e:
            logging.error("""
                The mounting was unsuccessfull with the exception:[Consult mount(8): manual for error codes e.g. 1= incorrect invocation, 64= partially unmounted, 0=success etc.]
                %s
                """ % (e)) 

    def unmount_PDrive_sable(self, logging):
        try:
            subprocess.check_call('sudo umount -f %s'%(self.p_Drive_mount_sable), shell=True)
        except Exception as e:
            logging.error("""
                The unmounting was unsuccessfull with the exception:
                %s
                """ % (e))

    def copy_file_pdrive(self, logging, source_path, dest_path):
        try:
            subprocess.check_call('sudo cp -r -f %s %s'%(source_path, dest_path), shell=True) 
        except Exception as e:
            logging.error("""
                The copy of file from local ./export to P_drive was unsuccessfull with the exception:
                %s
                """ % (e))
