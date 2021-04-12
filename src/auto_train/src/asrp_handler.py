# import command line parser

# import sys
#
# sys.path.append('/home/user/zhangxing/dcs_model_train_package_general_06052019/am/code/asrp_am/src')
# print [site_path for site_path in sys.path if 'site-packages' in site_path]

import argparse
import asrpAction
from asrpGlobal import *
import time

try:
    global asrp_starttime
    asrp_starttime = time.time()
    c_asrpGlobal.tempworkingdir = ""
    c_asrpGlobal.cmdargs_ossworkdir = ""

    # parse user input
    parser = argparse.ArgumentParser()

    # config and ossdir are not optional parameter
    parser.add_argument('--inputxmlfilename', action="store", required=True, help="input configure file")
    parser.add_argument('--ossworkdir', action="store", required=False,
                        help="oss directory to store your training debugging/results information")
    parser.add_argument('--host', action="store", help="oss host name")
    parser.add_argument('--id', action="store", help="oss id")
    parser.add_argument('--key', action="store", help="oss key")
    parser.add_argument('--debug', action="store_true", help="set to debug modem for debugging under windows")

    # parse odps
    parser.add_argument('--project', action='store', help='odps project name')
    parser.add_argument('--endpoint', action='store', help='odps endpoint')
    parser.add_argument('--u', action='store', help='odps accessid')
    parser.add_argument('--p', action='store', help='odps accesskey')
    parser.add_argument('--user', action='store', help='commit user')

    # other
    parser.add_argument('--logid', action='store', help='log id on oss')
    parser.add_argument('--printlogcode', action="store_true", help="whether to print the error and log code")


    inputargs = parser.parse_args()

    # execute the process
    asrpAction.Run(inputargs)

    if c_asrpGlobal.cmdargs_ossworkdir != "":
        pass
        # asrpOSS.asrpOSSPutFileToOSS(c_asrpGlobal.cmdargs_inputxmlfilename, asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,"done"))

except:
    pass
    # asrpLogError("Unexpected error %s" % asrpGetErrorMsg())

finally:
    pass
    # #copy log to OSS
    # if c_asrpGlobal.tempworkingdir != "" and c_asrpGlobal.cmdargs_ossworkdir != "":
    #     testName = ".".join(str(c_asrpGlobal.cmdargs_inputxmlfilename).strip().split("/")[-1].split('.')[:-1])
    #     asrpOSS.asrpOSSPutFileToOSS(c_asrpGlobal.cmdargs_inputxmlfilename, asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,"input",asrpGetFileNameExt(c_asrpGlobal.cmdargs_inputxmlfilename)))
    #     if os.path.isfile(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.tempworkingdir,"logoutput.txt")):
    #         asrpOSS.asrpOSSPutFileToOSS(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.tempworkingdir,"logoutput.txt"), asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,"logoutput.txt"))
    #     if os.path.isfile(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.tempworkingdir,"logerror.txt")):
    #         asrpOSS.asrpOSSPutFileToOSS(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.tempworkingdir,"logerror.txt"), asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,"logerror.txt"))
    #     asrpLogOutput('---res file : %s---'%str(os.path.exists(os.path.join(c_asrpGlobal.tempworkingdir,testName + '.cpr'))))
    #     if os.path.exists(os.path.join(c_asrpGlobal.tempworkingdir,testName + '.cpr')):
    #         asrpOSS.asrpOSSPutFileToOSS(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.tempworkingdir,testName + '.cpr'), asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,testName + '.cpr'))
    #     asrpLogOutput('---res file : %s---'%str(os.path.exists(os.path.join(c_asrpGlobal.tempworkingdir,testName + '.txt'))))
    #     if os.path.exists(os.path.join(c_asrpGlobal.tempworkingdir,testName + '.txt')):
    #         asrpOSS.asrpOSSPutFileToOSS(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.tempworkingdir,testName + '.txt'), asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,testName + '.txt'))
    # if c_asrpGlobal.tempworkingdir != "" and (not c_asrpGlobal.isDebugMode):
    #     asrpLogOutput("------remove %s----"%c_asrpGlobal.tempworkingdir)
    #     shutil.rmtree(c_asrpGlobal.tempworkingdir)
    # if c_asrpGlobal.cmdargs_ossworkdir != "":
    #     asrpOSS.asrpOSSDeleteObject(asrpJoinpathAccordingtoPathOS(c_asrpGlobal.cmdargs_ossworkdir,"running"))
    #     print "\n------------------------\nfinal outputs are in %s" % c_asrpGlobal.cmdargs_ossworkdir
    # asrp_endtime = time.time()
    # asrpLogOutput("\n------------------------\nstart time: %s\tend time: %s\telapsed time: %.3fh\n"%\
    #     (time.strftime("%Y%m%d %H:%M:%S", time.localtime(asrp_starttime)), time.strftime("%Y%m%d %H:%M:%S", time.localtime(asrp_endtime)), (asrp_endtime-asrp_starttime)/3600.0) )
