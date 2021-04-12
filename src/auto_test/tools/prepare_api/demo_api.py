from extract_train_data import DataPrepare
import json

if __name__ == '__main__':
    dp = DataPrepare()
    req_res = dp.prepare_data(prepare_type=1)

    res_dict = json.loads(req_res)

    prepare_uuid = res_dict['prepare_uuid']

    # do others
    # save prepare_uuid
    #

    data_path = ''
    while True:
        ready_res = dp.is_ready(prepare_uuid=prepare_uuid)
        res_dict = json.loads(ready_res)
        prepare_status = res_dict['prepare_status']
        if prepare_status == 1:
            data_path = res_dict['mock_data_path']

    print data_path
