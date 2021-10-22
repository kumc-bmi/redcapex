import os
import subprocess

class NetworkDrive:
    def __init__(self, p_Drive_path, p_Drive_mount_sable, p_Drive_domain, logging):
        ''' Constructor for this class. '''
        # Creating some member variables
        self.p_Drive_path = p_Drive_path
        self.p_Drive_mount_sable = p_Drive_mount_sable
        self.p_Drive_domain = p_Drive_domain
        self.logging = logging

    def mount(self, jnk_user, jnk_pass):
        try:
            subprocess.check_call('sudo mount -t cifs %s %s -o user=%s,domain=%s,password=%s'%(self.p_Drive_path, self.p_Drive_mount_sable, jnk_user, self.p_Drive_domain, jnk_pass), shell=True)
        except Exception as e:
            self.logging.error("""
                The mounting was unsuccessfull with the exception: 
                %s
                """ % (e)) 

    def unmount(self):
        try:
            subprocess.check_call('sudo umount -f %s'%(self.p_Drive_mount_sable), shell=True)
        except Exception as e:
            self.logging.error("""
                The unmounting was unsuccessfull with the exception:
                %s
                """ % (e))

    def copy_file(self, source_path, dest_path):
        try:
            subprocess.check_call('sudo cp -r -f %s %s'%(source_path, dest_path), shell=True) 
        except Exception as e:
            self.logging.error("""
                The copy of file from local %s to %s was unsuccessfull with the exception:
                %s
                """ % (source_path, dest_path, e))
