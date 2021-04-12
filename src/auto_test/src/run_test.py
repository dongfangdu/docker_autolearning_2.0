from ConfigParser import ConfigParser
from multiprocessing import Pool
import os
from tqdm import tqdm
import calculate_to_mysql
import clear_mysql
import generate_log
import move_log
import own_data_prepare
import parse_log_to_mysql
import replace_model
import report
import restfule_class


def lab(ini_path):
    cwd_path = os.path.abspath(os.path.dirname(__file__))
    _ini_path = os.path.join(cwd_path, '..', 'cfg', ini_path)
    cf = ConfigParser()
    cf.read(_ini_path)
    passwd = cf.get('EngineServer', 'passwd')
    label_txt = cf.get('Audio', 'label_txt_path')
    return passwd, label_txt


def run_test():
    passwd = lab('config.ini')[0]
    #os.system('echo %s|sudo -S chown -R admin:admin %s'%(passwd, os.path.abspath(os.path.join(os.getcwd(), "../.."))))
    # =================
    # 0.Clear Temp Table
    # =================
    try:
        clear_mysql.clear_unuseful_files('config.ini').Clear_files()
        generate_log.logger.info("clear temp table successful!")
    except Exception as exp:
        generate_log.logger.error("clear temp table failed!")
        generate_log.logger.error(exp.message)

        # =================
    # 1.Prepare Data
    # =================
    try:
        own_data_prepare.data_to_audio_table('config.ini').main()
        generate_log.logger.info("test data prepare successful!")
    except Exception as exp:
        generate_log.logger.error("test data prepare failed!")
        generate_log.logger.error(exp.message)

    # ================
    # 2.Replace Model
    # =================
    try:
        replace_model.rep_mol('config.ini').resetting()
        replace_model.rep_mol('config.ini').main()
        generate_log.logger.info("replace model successful!")
    except Exception as exp:
        generate_log.logger.error("replace model failed!")
        generate_log.logger.error(exp.message)

    # ================
    # 3.For Engine
    # =================
    cwd_path = os.path.abspath(os.path.dirname(__file__))
    os.system('sh %s/../src/restart_engine.sh' %(cwd_path))

    # ==================
    # 4.For Test
    # ==================
    try:
        restfule_class.to_sql('config.ini')
        generate_log.logger.info("test successful!")
    except Exception as exp:
        generate_log.logger.error("test failed!")
        generate_log.logger.error(exp.message)
		
    # ==================
    # 5.Move Log
    # ==================
    try:
        move_log.move_log('config.ini')
        generate_log.logger.info("move log successful!")
    except Exception as exp:
        generate_log.logger.error("move log failed!")
        generate_log.logger.error(exp.message)

    label_txt = lab('config.ini')[1]
    if label_txt != '':
        # ==================
        # 6.Data_to_Mysql
        # ==================
        try:
            parse_log_to_mysql.access_log_to_mysql('config.ini').main()
            generate_log.logger.info("parse log to mysql successful!")
        except Exception as exp:
            generate_log.logger.error("parse log to mysql failed!")
            generate_log.logger.error(exp.message)
        try:
            calculate_to_mysql.write_data_to_sql('config.ini').main()
            generate_log.logger.info("calculate result to mysql successful!")
        except Exception as exp:
            generate_log.logger.error("calculate result to mysql failed!")
            generate_log.logger.error(exp.message)

        # ===================
        # 7.Generate Report
        # ===================
        try:
            report.Write_Report('config.ini').main()
            generate_log.logger.info("generate report successful!")
        except Exception as exp:
            generate_log.logger.error("generate report failed!")
            generate_log.logger.error(exp.message)
    else:
        pass

    # ===================
    # 8. Clear Pcm and Recover Model
    # ===================
    try:
        replace_model.rep_mol('config.ini').resetting()
        generate_log.logger.info("recover model successful!")
    except Exception as exp:
        generate_log.logger.error("recover model failed!")
        generate_log.logger.error(exp.message)		



if __name__ == '__main__':
    run_test()
