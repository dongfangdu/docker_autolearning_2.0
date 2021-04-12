from ConfigParser import ConfigParser
import generate_log
import os
import json


class modify_conf():
    def __init__(self, ini_path):
        self.cwd_path = os.path.abspath(os.path.dirname(__file__))
        self.ini_path = os.path.join(self.cwd_path, '..', 'cfg', ini_path)
        self.cf = ConfigParser()
        self.cf.read(self.ini_path)
        self.engine_path = self.cf.get('Engine', 'engine').split(':')[1]
        self.conf_path = os.path.join(self.engine_path, 'service/resource/asr/default/conf/processor.json')

    def get_para(self):
        file = open(self.conf_path, "rb")
        fileJson = json.load(file) 	
        poster = fileJson['poster']
        poster_dis_fluency = poster['posters'][0]['enable']
        poster_add_punc = poster['posters'][1]['enable']
        poster_tag_punc = poster['posters'][2]['enable']
        conf = poster['posters'][3]['enable']
        nn_itn = poster['posters'][4]['enable']
        file.close()
        return poster_dis_fluency, poster_add_punc, poster_tag_punc, conf, nn_itn

    def modify(self):
        poster_dis_fluency, poster_add_punc, poster_tag_punc, conf, nn_itn = self.get_para()
        file = open(self.conf_path, "rb")
        fileJson = json.load(file)
        poster = fileJson['poster']
        poster['posters'][0]['enable'] = False
        poster['posters'][1]['enable'] = True
        poster['posters'][2]['enable'] = False
        poster['posters'][3]['enable'] = False
        poster['posters'][4]['enable'] = False
        file.close() 
        # print(fileJson)
        with open(self.conf_path, 'w') as f:
            json.dump(fileJson, f, indent=4)

    def recover(self):
        poster_dis_fluency, poster_add_punc, poster_tag_punc, conf, nn_itn = self.get_para()
        file = open(self.conf_path, "rb")
        fileJson = json.load(file)
        poster = fileJson['poster']
        poster['posters'][0]['enable'] = poster_dis_fluency
        poster['posters'][1]['enable'] = poster_add_punc
        poster['posters'][2]['enable'] = poster_tag_punc
        poster['posters'][3]['enable'] = conf
        poster['posters'][4]['enable'] = nn_itn
        file.close() 
        # print(fileJson)
        with open(self.conf_path, 'w') as f:
            json.dump(fileJson, f, indent=4)


if __name__ == '__main__':
    modify_conf('config.ini').modify()