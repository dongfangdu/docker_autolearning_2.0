import os
import generate_log
from ConfigParser import ConfigParser


def move_log(ini_path):
    cwd_path = os.path.abspath(os.path.dirname(__file__))
    _ini_path = os.path.join(cwd_path, '..', 'cfg', ini_path)
    cf = ConfigParser()
    cf.read(_ini_path)
    passwd = cf.get('EngineServer', 'passwd')
    engine = cf.get('Engine', 'engine').split(':')[0]
    engine_path = cf.get('Engine', 'engine').split(':')[1]
    asr_path = os.path.join(engine_path, 'service/logs/nls-cloud-asr')
    log_path = os.path.join(cf.get('Output', 'output_path'), 'SaveLog')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    os.system('cp -r %s %s' % (asr_path, log_path))

if __name__ == "__main__":
    #try:
        move_log('config.ini')
        generate_log.logger.info("move log successful!")
    #except Exception as exp:
        generate_log.logger.error("move log failed!")
        generate_log.logger.error(exp.message)
