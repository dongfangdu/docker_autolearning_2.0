自动训练

1、使用脚本时，于/cfg/config.ini 中，在[DataBase]下配置存储训练记录的数据库信息，在[FileSave]下配置存储训练生成模型的路径，在[RunShell]中配置训练包路径train_package,及训练包下拷出的原始配置文件的路径local_xml_dir (am_train_pipline的路径)，在[InitModel]下配置训练所需的基础模型的信息，此模型作为训练的起点模型

2、执行单轮训练时，在任意目录下直接运行/bin/am_train_pipline中的启动脚本，执行命令sh run_data_and_training.sh即可，推荐使用非root用户
