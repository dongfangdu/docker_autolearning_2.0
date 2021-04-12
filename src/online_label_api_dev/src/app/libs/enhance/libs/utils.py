# -*- coding: utf8 -*-
import json
import uuid


def get_json(status_code, vol_adj_path=None, final_save_path=None):
    output_dict = {"status_code": status_code, "vol_adj_path": vol_adj_path, "final_save_path": final_save_path}
    result = json.dumps(output_dict)
    return result


def get_uuid():
    guid = uuid.uuid4()
    return str(guid).replace('-', '')
