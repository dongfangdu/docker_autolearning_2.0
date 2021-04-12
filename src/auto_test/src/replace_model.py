# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 09:22:26 2019

@author: 123
"""
import shutil
from ConfigParser import ConfigParser
import generate_log
import os


class rep_mol():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.passwd = self.cf.get('EngineServer', 'passwd')
        self.engine = self.cf.get('Engine', 'engine').split(':')[0]
        if self.engine == '2.0':
            self.engine_path = os.path.join(self.cf.get('Engine', 'engine').split(':')[1],
                                            'service/resource/asr/default/models')
        elif self.engine == '1.0':
            self.engine_path = os.path.join(self.cf.get('Engine', 'engine').split(':')[1], 'models/alisr_model')
        self.am_model = os.path.join(self.engine_path, 'am/fsmn.net')
        self.lm_model = os.path.join(self.engine_path, 'lm/main_lm')
        self.am_basis_model = os.path.join(os.path.dirname(self.am_model), 'fsmn.basis')
        self.lm_basis_model = os.path.join(os.path.dirname(self.lm_model), 'lm_basis')
        self.temp_model_path = os.path.join(os.path.dirname(os.getcwd()), 'temp', 'model')
        self.replaced_am_model = self.cf.get('Models', 'am_model')
        self.replaced_lm_model = self.cf.get('Models', 'lm_model')
        
    def replace_am_model(self, replaced_am_model):
        os.rename(self.am_model, self.am_basis_model)
        shutil.copy(replaced_am_model, self.temp_model_path)
        #os.rename(os.path.join(self.temp_model_path, os.path.basename(replaced_am_model)),
        #          os.path.join(os.path.dirname(self.am_model), 'fsmn.net'))
	#print('rm -f %s' %(os.path.join(os.path.dirname(self.am_model), 'fsmn.net')))
	#print('cp %s %s' %(os.path.join(self.temp_model_path, os.path.basename(replaced_am_model)),
        #           os.path.join(os.path.dirname(self.am_model), 'fsmn.net')))
	os.system('rm -f %s' %(os.path.join(os.path.dirname(self.am_model), 'fsmn.net')))
	os.system('cp %s %s' %(os.path.join(self.temp_model_path, os.path.basename(replaced_am_model)),
                   os.path.join(os.path.dirname(self.am_model), 'fsmn.net')))

    def replace_lm_model(self, replaced_lm_model):
        os.rename(self.lm_model, self.lm_basis_model)
        shutil.copytree(replaced_lm_model, os.path.join(self.temp_model_path, os.path.basename(replaced_lm_model)))
        os.rename(os.path.join(self.temp_model_path, os.path.basename(replaced_lm_model)),
                  os.path.join(os.path.dirname(self.lm_model), 'main_lm'))

    def recover_am_model(self):
        if os.path.exists(self.am_basis_model):
            try:
                os.remove(self.am_model)
            except:
                pass
            os.rename(self.am_basis_model, self.am_model)

    def recover_lm_model(self):
        if os.path.exists(self.lm_basis_model):
            try:
                shutil.rmtree(self.lm_model)
            except:
                pass
            os.rename(self.lm_basis_model, self.lm_model)

    def resetting(self):
        self.recover_am_model()
        self.recover_lm_model()

    def msg(self):
        return self.am_model, self.ini_path

    def main(self):
        if os.path.exists(self.temp_model_path):
            shutil.rmtree(self.temp_model_path)
        os.makedirs(self.temp_model_path)
        #os.system('echo %s|sudo -S chmod -R 777 %s'%(self.passwd, self.temp_model_path))
        #os.system('echo %s|sudo -S chown -R admin:admin %s'%(self.passwd, self.temp_model_path))
        if self.replaced_am_model != '':
            self.replace_am_model(self.replaced_am_model)
        if self.replaced_lm_model != '':
            self.replace_lm_model(self.replaced_lm_model)
     
if __name__ == '__main__':
    #try:
        rep_mol('config.ini').resetting()
        rep_mol('config.ini').main()
        generate_log.logger.info("replace model successful!")
    #except Exception as exp:
        generate_log.logger.error("replace model failed!")
        generate_log.logger.error(exp.message)

