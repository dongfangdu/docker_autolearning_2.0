from ConfigParser import ConfigParser
import generate_log
import os
import replace_model

class con_and_rep():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
		
    def con(self):
        ip = self.cf.get('RemoteServer', 'host')
        port = self.cf.get('RemoteServer', 'port')
        user = self.cf.get('RemoteServer', 'user')
        passwd = self.cf.get('RemoteServer', 'passwd')
        remote_connection = paramiko.Transport((ip, int(port)))
        remote_connection.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(remote_connection)
        remote_file_path = '/home/auto_test'
		sftp.put(os.path.join(os.path.dirname(os.getcwd()), remote_file_path)
        src_path = os.path.join(remote_file_path, 'src')
        remote_connection.exec_command('cd %s'%src_path)
        remote_connection.exec_command('python rep_and_res.py')
		
if __name__ == '__main__':
    con_and_rep('business_config.ini').con()