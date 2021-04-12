from ConfigParser import ConfigParser
import generate_log
import os
import replace_model

class con_and_rep():
    def __init__(self, ini_path):
        self.ini_name = ini_path
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)

    def rep(self):
        try:
            replace_model.rep_mol(self.ini_name).main()
            generate_log.logger.info("replace model in business engine successful!")
        except Exception as exp:
            generate_log.logger.error("replace model in business engine failed!")
            generate_log.logger.error(exp.message)
			
    def res(self):
        os.system('sh ./restart_engine.sh')
		
    def main(self):
        self.rep()
        self.res()
		
if __name__ == '__main__':
    con_and_rep('business_config.ini').main()    
		
