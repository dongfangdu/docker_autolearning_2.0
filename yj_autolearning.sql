-- MySQL dump 10.14  Distrib 5.5.64-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: yj_autolearning_engine
-- ------------------------------------------------------
-- Server version	5.6.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `yj_autolearning_engine`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `yj_autolearning_engine` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `yj_autolearning_engine`;

--
-- Table structure for table `al_audiosrc_fileinfo`
--

DROP TABLE IF EXISTS `al_audiosrc_fileinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_audiosrc_fileinfo` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `asrc_uuid` varchar(64) NOT NULL,
  `asrc_url` varchar(512) NOT NULL,
  `asrc_md5` varchar(64) NOT NULL,
  `asrc_size` int(11) NOT NULL,
  `asrc_mime_type` varchar(32) NOT NULL,
  `asrc_rel_path` varchar(512) DEFAULT NULL,
  `asrc_upload_time` int(11) DEFAULT NULL,
  `upload_uuid` varchar(64) DEFAULT NULL,
  `upload_dir` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_asrc_uuid` (`asrc_uuid`),
  KEY `idx_asrc_upload_time` (`asrc_upload_time`),
  KEY `idx_asrc_md5_size` (`asrc_md5`,`asrc_size`)
) ENGINE=InnoDB AUTO_INCREMENT=3348 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_audiosrc_fileinfo`
--

LOCK TABLES `al_audiosrc_fileinfo` WRITE;
/*!40000 ALTER TABLE `al_audiosrc_fileinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_audiosrc_fileinfo` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_audiosrc_fileinfo_BEFORE_INSERT` BEFORE INSERT ON `al_audiosrc_fileinfo` FOR EACH ROW
BEGIN
    IF NEW.insert_time IS NULL THEN 
    
        SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_audiosrc_filetrans`
--

DROP TABLE IF EXISTS `al_audiosrc_filetrans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_audiosrc_filetrans` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ng_version` varchar(64) NOT NULL COMMENT '引擎版本号',
  `file_uuid` varchar(64) NOT NULL,
  `file_unikey` varchar(64) DEFAULT NULL,
  `file_url` varchar(512) DEFAULT NULL,
  `ft_task_id` varchar(64) DEFAULT NULL,
  `ft_status_code` varchar(64) DEFAULT NULL,
  `ft_status_text` varchar(500) DEFAULT NULL,
  `recog_uuid` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ft_task_id` (`ft_task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2397 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_audiosrc_filetrans`
--

LOCK TABLES `al_audiosrc_filetrans` WRITE;
/*!40000 ALTER TABLE `al_audiosrc_filetrans` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_audiosrc_filetrans` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_audiosrc_filetrans_BEFORE_INSERT` BEFORE INSERT ON `al_audiosrc_filetrans` FOR EACH ROW
BEGIN
    IF NEW.insert_time IS NULL THEN 
    
        SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_ng_bak_files`
--

DROP TABLE IF EXISTS `al_ng_bak_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_ng_bak_files` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `file_name` varchar(128) NOT NULL COMMENT '备份后的文件名，包括后缀名，但不包括路径',
  `path` varchar(1024) NOT NULL COMMENT '备份后的文件绝对路径',
  `origin_st_mtime` int(11) NOT NULL COMMENT '备份之前文件的最后修改时间',
  `st_size` int(11) NOT NULL COMMENT '文件大小，单位：字节',
  `type` varchar(16) NOT NULL COMMENT 'alisr=1,trace=2,access=3,diting=4,diting_access=5,audio=6',
  `ng_version` varchar(64) DEFAULT NULL COMMENT '引擎版本号',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uni_name_time` (`file_name`,`origin_st_mtime`) USING BTREE COMMENT '文件名+最后修改时间'
) ENGINE=InnoDB AUTO_INCREMENT=179704 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_ng_bak_files`
--

LOCK TABLES `al_ng_bak_files` WRITE;
/*!40000 ALTER TABLE `al_ng_bak_files` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_ng_bak_files` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_ng_bak_files_BEFORE_INSERT` BEFORE INSERT ON `al_ng_bak_files` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_ng_diting`
--

DROP TABLE IF EXISTS `al_ng_diting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_ng_diting` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `start_time` datetime(3) DEFAULT NULL COMMENT 'diting语句识别的开始时间',
  `uuid` varchar(64) NOT NULL COMMENT 'ditting与客户端之间的请求id',
  `request_id` varchar(64) NOT NULL COMMENT 'ditting与asr之间的请求id，即语句id',
  `end_time` datetime(3) DEFAULT NULL COMMENT 'diting语句识别的结束时间',
  `http_cost_time` int(11) DEFAULT NULL COMMENT 'diting到asr的http传输时延，单位：毫秒',
  `trans_delay` int(11) DEFAULT NULL COMMENT '客户端到diting之间的传输时延',
  `related_status` smallint(1) DEFAULT '0' COMMENT '是否已经完成trans_delay的计算，0-未完成；1-已完成',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_request_id` (`request_id`) USING BTREE COMMENT '语句id',
  KEY `idx_uuid` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_ng_diting`
--

LOCK TABLES `al_ng_diting` WRITE;
/*!40000 ALTER TABLE `al_ng_diting` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_ng_diting` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_ng_diting_BEFORE_INSERT` BEFORE INSERT ON `al_ng_diting` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_ng_diting_relation`
--

DROP TABLE IF EXISTS `al_ng_diting_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_ng_diting_relation` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `time` datetime(3) DEFAULT NULL COMMENT '从mongodb中获取，该记录的保存时间',
  `uuid` varchar(64) NOT NULL COMMENT 'ditting与客户端之间的业务请求id',
  `line_id` varchar(128) DEFAULT NULL COMMENT '从mongodb中获取，role_id@court_id@case_id',
  `case_id` varchar(64) DEFAULT NULL COMMENT '案件id，从mongodb中获取',
  `court_id` varchar(64) DEFAULT NULL COMMENT '法庭id，从mongodb中获取',
  `role_id` varchar(64) DEFAULT NULL COMMENT '角色id，从mongodb中获取',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uuid` (`uuid`) USING BTREE COMMENT 'diting与客户端之间的连接id做唯一索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_ng_diting_relation`
--

LOCK TABLES `al_ng_diting_relation` WRITE;
/*!40000 ALTER TABLE `al_ng_diting_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_ng_diting_relation` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_ng_diting_relation_BEFORE_INSERT` BEFORE INSERT ON `al_ng_diting_relation` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_ng_trans_delay_info`
--

DROP TABLE IF EXISTS `al_ng_trans_delay_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_ng_trans_delay_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `line_id` varchar(128) NOT NULL COMMENT '从mongodb中获取，role_id@court_id@case_id',
  `case_id` varchar(64) DEFAULT NULL COMMENT '案件id，从mongodb中获取',
  `role_id` varchar(64) DEFAULT NULL COMMENT '角色id，从mongodb中获取',
  `court_id` varchar(64) DEFAULT NULL COMMENT '法庭id，从mongodb中获取',
  `pkg_cnt` int(11) NOT NULL COMMENT '音频数据包的数量，从mongodb中获取',
  `send_time` datetime(3) NOT NULL COMMENT '音频数据包的发送时间，从mongodb中获取',
  `receive_time` datetime(3) NOT NULL COMMENT '音频数据包的接收时间，从mongodb中获取',
  `delay` int(11) NOT NULL COMMENT 'receive_time和send_time的时间差（单位：毫秒）',
  `related_status` smallint(1) DEFAULT '0' COMMENT '是否已关联到diting的语句id，0-未关联；1-已关联',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_line_id_time` (`line_id`,`send_time`) USING BTREE COMMENT 'line_id和send_time'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_ng_trans_delay_info`
--

LOCK TABLES `al_ng_trans_delay_info` WRITE;
/*!40000 ALTER TABLE `al_ng_trans_delay_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_ng_trans_delay_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_ng_trans_delay_info_BEFORE_INSERT` BEFORE INSERT ON `al_ng_trans_delay_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_prepare_choice_param`
--

DROP TABLE IF EXISTS `al_prepare_choice_param`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_prepare_choice_param` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `request_id` varchar(64) NOT NULL,
  `choice_type` smallint(6) NOT NULL COMMENT '筛选值计算的类型，1为根据rtf和困惑度预测的wer',
  `choice_value` decimal(8,3) DEFAULT NULL COMMENT '筛选计算值',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uni_request_id_choice_type` (`request_id`,`choice_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_prepare_choice_param`
--

LOCK TABLES `al_prepare_choice_param` WRITE;
/*!40000 ALTER TABLE `al_prepare_choice_param` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_prepare_choice_param` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_prepare_choice_param_BEFORE_INSERT` BEFORE INSERT ON `al_prepare_choice_param` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_prepare_choice_rule`
--

DROP TABLE IF EXISTS `al_prepare_choice_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_prepare_choice_rule` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `choice_type` smallint(6) NOT NULL COMMENT '筛选值计算的类型，1为根据rtf和困惑度预测的wer',
  `rule_logic` varchar(10) DEFAULT NULL,
  `rule_op_type` varchar(10) DEFAULT NULL,
  `rule_op_threshold` decimal(8,3) DEFAULT NULL,
  `rule_order` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_prepare_choice_rule`
--

LOCK TABLES `al_prepare_choice_rule` WRITE;
/*!40000 ALTER TABLE `al_prepare_choice_rule` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_prepare_choice_rule` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_prepare_choice_rule_BEFORE_INSERT` BEFORE INSERT ON `al_prepare_choice_rule` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_prepare_data_info`
--

DROP TABLE IF EXISTS `al_prepare_data_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_prepare_data_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `prepare_uuid` varchar(64) NOT NULL,
  `pdata_uuid` varchar(64) NOT NULL,
  `pdata_src_type` smallint(6) NOT NULL,
  `pdata_url` varchar(255) NOT NULL,
  `pdata_text` varchar(1024) NOT NULL,
  `request_id` varchar(64) DEFAULT NULL,
  `uttr_url` varchar(255) DEFAULT NULL,
  `uttr_result` varchar(1024) DEFAULT NULL,
  `uttr_duration` int(11) DEFAULT NULL,
  `label_uuid` varchar(64) DEFAULT NULL,
  `label_text` varchar(1024) DEFAULT NULL,
  `enhance_code` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_prepare_uuid` (`prepare_uuid`) USING BTREE,
  KEY `idx_request_id` (`request_id`) USING BTREE,
  KEY `idx_label_uuid` (`label_uuid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2940683 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_prepare_data_info`
--

LOCK TABLES `al_prepare_data_info` WRITE;
/*!40000 ALTER TABLE `al_prepare_data_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_prepare_data_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_prepare_data_info_BEFORE_INSERT` BEFORE INSERT ON `al_prepare_data_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_prepare_request_info`
--

DROP TABLE IF EXISTS `al_prepare_request_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_prepare_request_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prepare_uuid` varchar(64) NOT NULL,
  `prepare_start_time` int(11) DEFAULT NULL,
  `prepare_finish_time` int(11) DEFAULT NULL,
  `prepare_status` smallint(6) NOT NULL DEFAULT '0',
  `prepare_type` smallint(6) NOT NULL,
  `prepare_data_path` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `uni_prepare_uuid` (`prepare_uuid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1699 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_prepare_request_info`
--

LOCK TABLES `al_prepare_request_info` WRITE;
/*!40000 ALTER TABLE `al_prepare_request_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_prepare_request_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_prepare_request_info_BEFORE_INSERT` BEFORE INSERT ON `al_prepare_request_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_utterance_access`
--

DROP TABLE IF EXISTS `al_utterance_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_utterance_access` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `ng_version` varchar(64) NOT NULL COMMENT '引擎版本号',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` varchar(64) NOT NULL COMMENT '语句id',
  `time` datetime NOT NULL COMMENT '语句识别的结束时间',
  `app` varchar(64) DEFAULT NULL,
  `group` varchar(64) DEFAULT NULL,
  `ip` varchar(16) DEFAULT NULL COMMENT '客户端ip',
  `app_key` varchar(64) DEFAULT NULL,
  `session_id` varchar(64) DEFAULT NULL,
  `device_uuid` varchar(64) DEFAULT NULL,
  `uid` varchar(64) DEFAULT NULL,
  `start_timestamp` varchar(13) DEFAULT NULL COMMENT '语句识别的开始时间',
  `latency` int(8) DEFAULT NULL COMMENT '时延',
  `status_code` varchar(16) DEFAULT NULL,
  `status_message` varchar(1024) DEFAULT NULL,
  `backend_apps` varchar(255) DEFAULT NULL,
  `duration` int(8) DEFAULT NULL,
  `audio_format` varchar(32) DEFAULT NULL,
  `audio_url` varchar(255) DEFAULT NULL COMMENT '未知',
  `sample_rate` int(16) DEFAULT NULL COMMENT '采样率，单位：1000',
  `method` varchar(64) DEFAULT NULL,
  `packet_count` int(8) DEFAULT NULL,
  `avg_packet_duration` int(8) DEFAULT NULL,
  `total_rtf` decimal(8,3) DEFAULT NULL,
  `raw_rtf` decimal(8,3) DEFAULT NULL,
  `real_rtf` decimal(8,3) DEFAULT NULL COMMENT '识别速率',
  `detect_duration` int(8) DEFAULT NULL COMMENT '语句时长',
  `total_cost_time` int(8) DEFAULT NULL,
  `receive_cost_time` int(8) DEFAULT NULL,
  `wait_cost_time` int(8) DEFAULT NULL,
  `process_time` int(8) DEFAULT NULL,
  `processor_id` int(8) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `vocabulary_id` varchar(64) DEFAULT NULL,
  `keyword_list_id` varchar(64) DEFAULT NULL,
  `customization_id` varchar(64) DEFAULT NULL,
  `class_vocabulary_id` varchar(64) DEFAULT NULL,
  `result` varchar(1024) NOT NULL COMMENT '识别结果',
  `group_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uni_request_id` (`request_id`),
  KEY `idx_time` (`time`) USING BTREE,
  KEY `idx_request_id` (`request_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=245444 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_utterance_access`
--

LOCK TABLES `al_utterance_access` WRITE;
/*!40000 ALTER TABLE `al_utterance_access` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_utterance_access` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_utterance_access_BEFORE_INSERT` BEFORE INSERT ON `al_utterance_access` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_utterance_audio`
--

DROP TABLE IF EXISTS `al_utterance_audio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_utterance_audio` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` varchar(50) NOT NULL COMMENT '语句id',
  `path` varchar(255) NOT NULL COMMENT '语句音频文件原始的',
  `url` varchar(255) NOT NULL COMMENT '语句音频文件的url',
  `truncation_ratio` decimal(8,4) DEFAULT NULL COMMENT '语句音频文件的截幅比',
  `volume` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的音量',
  `snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的信噪比',
  `pre_snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的前信噪比',
  `post_snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的后信噪比',
  `is_assigned` smallint(6) NOT NULL DEFAULT '0' COMMENT '是否被分配去标注的标识：0-未分配，1-已分配',
  `uttr_status` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uni_request_id` (`request_id`) USING BTREE,
  KEY `idx_request_id` (`request_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=176557 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_utterance_audio`
--

LOCK TABLES `al_utterance_audio` WRITE;
/*!40000 ALTER TABLE `al_utterance_audio` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_utterance_audio` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_engine`.`al_utterance_audio_BEFORE_INSERT` BEFORE INSERT ON `al_utterance_audio` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `yj_autolearning_label`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `yj_autolearning_label` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `yj_autolearning_label`;

--
-- Table structure for table `al_labelraw_result`
--

DROP TABLE IF EXISTS `al_labelraw_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_labelraw_result` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label_uuid` varchar(64) NOT NULL COMMENT '每次标注的全局ID',
  `label_text` varchar(500) DEFAULT NULL COMMENT '标注文本',
  `label_time` int(11) DEFAULT NULL COMMENT '标注时间',
  `label_counter` int(11) DEFAULT '1',
  `request_id` varchar(50) NOT NULL COMMENT '语句全局ID',
  `uttr_url` varchar(255) NOT NULL COMMENT '语句相对路径（冗余）：\nal_utterance.url',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uni_label_uuid` (`label_uuid`),
  KEY `idx_request_id` (`request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=69452 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT COMMENT='标注日志表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_labelraw_result`
--

LOCK TABLES `al_labelraw_result` WRITE;
/*!40000 ALTER TABLE `al_labelraw_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_labelraw_result` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_label`.`al_labelraw_result_BEFORE_INSERT` BEFORE INSERT ON `al_labelraw_result` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_labelraw_tag_map`
--

DROP TABLE IF EXISTS `al_labelraw_tag_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_labelraw_tag_map` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label_uuid` varchar(64) NOT NULL COMMENT '每次标注的全局ID',
  `tag_uuid` varchar(500) DEFAULT NULL COMMENT '标签全局ID',
  `tag_name` int(11) DEFAULT NULL COMMENT '标签内容',
  `tag_ikey` varchar(50) NOT NULL COMMENT '标签内容索引：使用自定义的crc64函数来哈希tag_name',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_tag_ikey` (`tag_ikey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT COMMENT='标注标签关系表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_labelraw_tag_map`
--

LOCK TABLES `al_labelraw_tag_map` WRITE;
/*!40000 ALTER TABLE `al_labelraw_tag_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_labelraw_tag_map` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_label`.`al_labelraw_tag_map_BEFORE_INSERT` BEFORE INSERT ON `al_labelraw_tag_map` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_labelraw_utterance_info`
--

DROP TABLE IF EXISTS `al_labelraw_utterance_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_labelraw_utterance_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL,
  `ng_version` varchar(64) NOT NULL COMMENT '引擎版本号',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` varchar(64) NOT NULL COMMENT '语句id',
  `time` datetime NOT NULL COMMENT '语句识别的结束时间',
  `app` varchar(64) DEFAULT NULL,
  `group` varchar(64) DEFAULT NULL,
  `ip` varchar(16) DEFAULT NULL COMMENT '客户端ip',
  `app_key` varchar(64) DEFAULT NULL,
  `session_id` varchar(64) DEFAULT NULL,
  `device_uuid` varchar(64) DEFAULT NULL,
  `uid` varchar(64) DEFAULT NULL,
  `start_timestamp` varchar(13) DEFAULT NULL COMMENT '语句识别的开始时间',
  `latency` int(8) DEFAULT NULL COMMENT '时延',
  `status_code` varchar(16) DEFAULT NULL,
  `status_message` varchar(1024) DEFAULT NULL,
  `backend_apps` varchar(255) DEFAULT NULL,
  `duration` int(8) DEFAULT NULL,
  `audio_format` varchar(32) DEFAULT NULL,
  `audio_url` varchar(255) DEFAULT NULL COMMENT '未知',
  `sample_rate` int(16) DEFAULT NULL COMMENT '采样率，单位：1000',
  `method` varchar(64) DEFAULT NULL,
  `packet_count` int(8) DEFAULT NULL,
  `avg_packet_duration` int(8) DEFAULT NULL,
  `total_rtf` decimal(8,3) DEFAULT NULL,
  `raw_rtf` decimal(8,3) DEFAULT NULL,
  `real_rtf` decimal(8,3) DEFAULT NULL COMMENT '识别速率',
  `detect_duration` int(8) DEFAULT NULL COMMENT '语句时长',
  `total_cost_time` int(8) DEFAULT NULL,
  `receive_cost_time` int(8) DEFAULT NULL,
  `wait_cost_time` int(8) DEFAULT NULL,
  `process_time` int(8) DEFAULT NULL,
  `processor_id` int(8) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `vocabulary_id` varchar(64) DEFAULT NULL,
  `keyword_list_id` varchar(64) DEFAULT NULL,
  `customization_id` varchar(64) DEFAULT NULL,
  `class_vocabulary_id` varchar(64) DEFAULT NULL,
  `result` varchar(1024) NOT NULL COMMENT '识别结果',
  `group_name` varchar(64) DEFAULT NULL,
  `path` varchar(255) NOT NULL COMMENT '语句音频文件原始的',
  `url` varchar(255) NOT NULL COMMENT '语句音频文件的url',
  `truncation_ratio` decimal(8,4) DEFAULT NULL COMMENT '语句音频文件的截幅比',
  `volume` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的音量',
  `snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的信噪比',
  `pre_snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的前信噪比',
  `post_snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的后信噪比',
  `uttr_status` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uni_request_id` (`request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=69452 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_labelraw_utterance_info`
--

LOCK TABLES `al_labelraw_utterance_info` WRITE;
/*!40000 ALTER TABLE `al_labelraw_utterance_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_labelraw_utterance_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_label`.`al_labelraw_utterance_info_BEFORE_INSERT` BEFORE INSERT ON `al_labelraw_utterance_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `yj_autolearning_test`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `yj_autolearning_test` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `yj_autolearning_test`;

--
-- Table structure for table `al_test_asr_audio_info`
--

DROP TABLE IF EXISTS `al_test_asr_audio_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_test_asr_audio_info` (
  `insert_time` int(255) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `data_uuid` varchar(255) DEFAULT NULL COMMENT '测试数据uuid',
  `prepare_uuid` varchar(255) DEFAULT NULL COMMENT '测试数据准备uuid',
  `request_id` varchar(50) NOT NULL COMMENT '语音识别的请求id（初始音频的名称，不是日志里的request_id）',
  `path` varchar(255) NOT NULL COMMENT '音频文件的完整路径',
  `url` varchar(255) DEFAULT NULL COMMENT 'url',
  `cut_ratio` decimal(8,4) DEFAULT NULL COMMENT '截幅比',
  `volume` decimal(8,2) DEFAULT NULL COMMENT '音量',
  `snr` decimal(8,2) DEFAULT NULL COMMENT '信噪比',
  `pre_snr` decimal(8,2) DEFAULT NULL COMMENT '前信噪比',
  `latter_snr` decimal(8,2) DEFAULT NULL COMMENT '后信噪比',
  `label_text` varchar(1024) DEFAULT NULL COMMENT '标注文本',
  `person` varchar(255) DEFAULT NULL COMMENT '标注的人名',
  `accent` varchar(255) DEFAULT NULL COMMENT '标注的口音',
  `gender` tinyint(2) DEFAULT NULL COMMENT '标注的性别',
  `task_id` varchar(255) DEFAULT NULL COMMENT 'restful识别的请求id',
  `res_text` text COMMENT '引擎识别文本',
  `par_log_text` varchar(255) DEFAULT NULL COMMENT '日志解析识别文本',
  `tot_words` int(11) DEFAULT NULL COMMENT 'total_words：总字数',
  `cor_words` int(11) DEFAULT NULL COMMENT 'correct_words：测试结果与标注结果相同字数',
  `word_cor_rate` decimal(8,2) DEFAULT NULL COMMENT 'word_correct_rate：测试结果与标注结果相同字数占总字数比率',
  `word_err_rate` decimal(8,2) DEFAULT NULL COMMENT 'word_error_rate：测试结果与标注结果不相同字数占总字数比率',
  `ins_cnt` int(11) DEFAULT NULL COMMENT 'insertion_count：错误类型为插入错误的总字数',
  `del_cnt` int(11) DEFAULT NULL COMMENT 'delete_count：错误类型为删除错误的总字数',
  `sub_cnt` int(11) DEFAULT NULL COMMENT 'sub_cnt：错误类型为替换错误的总字数',
  `total_rtf` decimal(8,3) DEFAULT NULL COMMENT '总时间/音频时长',
  `raw_rtf` decimal(8,3) DEFAULT NULL COMMENT '等待时间/音频时长',
  `real_rtf` decimal(8,3) DEFAULT NULL COMMENT '识别时间/音频时长',
  `duration` int(255) DEFAULT NULL COMMENT '等待时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `request_id` (`request_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=16481 DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_test_asr_audio_info`
--

LOCK TABLES `al_test_asr_audio_info` WRITE;
/*!40000 ALTER TABLE `al_test_asr_audio_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_test_asr_audio_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_test`.`al_test_asr_audio_info_BEFORE_INSERT` BEFORE INSERT ON `al_test_asr_audio_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_test_overall_results`
--

DROP TABLE IF EXISTS `al_test_overall_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_test_overall_results` (
  `insert_time` int(255) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `test_id` varchar(255) DEFAULT NULL COMMENT '测试全局id',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `model_uuid` varchar(255) DEFAULT NULL COMMENT '测试模型全局ID',
  `model_url` varchar(255) DEFAULT NULL COMMENT '测试模型绝对路劲',
  `data_uuid` varchar(255) DEFAULT NULL COMMENT '测试数据全局ID',
  `word_err_rate` decimal(8,2) DEFAULT NULL COMMENT 'word_error_rate：字错误率',
  `tot_word_err_cnt` int(11) DEFAULT NULL COMMENT 'total_word_error_number：总错误字数',
  `tot_word_cnt` int(11) DEFAULT NULL COMMENT 'total_word_number：总字数',
  `ins_cnt` int(11) DEFAULT NULL COMMENT 'insertion_count：错误类型为插入错误的总字数',
  `del_cnt` int(11) DEFAULT NULL COMMENT 'delete_count：错误类型为删除错误的总字数',
  `sub_cnt` int(11) DEFAULT NULL COMMENT 'sub_count：错误类型为替换错误的总字数',
  `sent_err_rate` decimal(8,2) DEFAULT NULL COMMENT 'sentence_error_rate：句错误率',
  `err_sent_cnt` int(11) DEFAULT NULL COMMENT 'incorrect_sentence_number：识别与标注结果不一致的句子数',
  `tot_sent_cnt` int(11) DEFAULT NULL COMMENT 'total_sentence_number：总句数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=219 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_test_overall_results`
--

LOCK TABLES `al_test_overall_results` WRITE;
/*!40000 ALTER TABLE `al_test_overall_results` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_test_overall_results` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_test`.`al_test_overall_results_BEFORE_INSERT` BEFORE INSERT ON `al_test_overall_results` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_test_overall_results_copy`
--

DROP TABLE IF EXISTS `al_test_overall_results_copy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_test_overall_results_copy` (
  `insert_time` int(255) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `test_id` varchar(255) DEFAULT NULL COMMENT '测试全局id',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `model_uuid` varchar(255) DEFAULT NULL COMMENT '测试模型全局ID',
  `model_url` varchar(255) DEFAULT NULL COMMENT '测试模型绝对路劲',
  `data_uuid` varchar(255) DEFAULT NULL COMMENT '测试数据全局ID',
  `word_err_rate` decimal(8,2) DEFAULT NULL COMMENT 'word_error_rate：字错误率',
  `tot_word_err_cnt` int(11) DEFAULT NULL COMMENT 'total_word_error_number：总错误字数',
  `tot_word_cnt` int(11) DEFAULT NULL COMMENT 'total_word_number：总字数',
  `ins_cnt` int(11) DEFAULT NULL COMMENT 'insertion_count：错误类型为插入错误的总字数',
  `del_cnt` int(11) DEFAULT NULL COMMENT 'delete_count：错误类型为删除错误的总字数',
  `sub_cnt` int(11) DEFAULT NULL COMMENT 'sub_count：错误类型为替换错误的总字数',
  `sent_err_rate` decimal(8,2) DEFAULT NULL COMMENT 'sentence_error_rate：句错误率',
  `err_sent_cnt` int(11) DEFAULT NULL COMMENT 'incorrect_sentence_number：识别与标注结果不一致的句子数',
  `tot_sent_cnt` int(11) DEFAULT NULL COMMENT 'total_sentence_number：总句数',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_test_overall_results_copy`
--

LOCK TABLES `al_test_overall_results_copy` WRITE;
/*!40000 ALTER TABLE `al_test_overall_results_copy` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_test_overall_results_copy` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `al_test_overall_results_BEFORE_INSERT_copy` BEFORE INSERT ON `al_test_overall_results_copy` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_test_result_by_sentence`
--

DROP TABLE IF EXISTS `al_test_result_by_sentence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_test_result_by_sentence` (
  `insert_time` int(255) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `test_id` varchar(255) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `model_uuid` varchar(255) DEFAULT NULL COMMENT '测试模型全局ID',
  `data_uuid` varchar(255) DEFAULT NULL COMMENT '测试数据全局ID',
  `task_id` varchar(255) DEFAULT NULL COMMENT 'restful识别的请求id',
  `request_id` varchar(255) DEFAULT NULL COMMENT '语音识别的请求id（初始音频的名称，不是日志里的request_id）',
  `path` varchar(255) DEFAULT NULL COMMENT '音频文件的完整路径',
  `url` varchar(255) DEFAULT NULL COMMENT '音频文件相对路径',
  `tot_words` int(11) DEFAULT NULL COMMENT 'total_words：总字数',
  `cor_words` int(11) DEFAULT NULL COMMENT 'correct_words：测试结果与标注结果相同字数',
  `word_cor_rate` decimal(8,2) DEFAULT NULL COMMENT 'word_correct_rate：测试结果与标注结果相同字数占总字数比率',
  `word_err_rate` decimal(8,2) DEFAULT NULL COMMENT 'word_error_rate：测试结果与标注结果不相同字数占总字数比率',
  `ins_cnt` int(11) DEFAULT NULL COMMENT 'insertion_count：错误类型为插入错误的总字数',
  `del_cnt` int(11) DEFAULT NULL COMMENT 'delete_count：错误类型为删除错误的总字数',
  `sub_cnt` int(11) DEFAULT NULL COMMENT 'sub_cnt：错误类型为替换错误的总字数',
  `label_text` varchar(1024) DEFAULT NULL COMMENT '人工标注文本',
  `recog_text` varchar(1024) DEFAULT '' COMMENT '引擎识别文本',
  `par_log_text` varchar(1024) DEFAULT NULL COMMENT '日志解析识别文本',
  `total_rtf` decimal(8,2) DEFAULT NULL COMMENT '总时间/音频时长',
  `raw_rtf` decimal(8,2) DEFAULT NULL COMMENT '等待时间/音频时长',
  `real_rtf` decimal(8,2) DEFAULT NULL COMMENT '识别时间/音频时长',
  `duration` decimal(8,2) DEFAULT NULL COMMENT '等待时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=244759 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_test_result_by_sentence`
--

LOCK TABLES `al_test_result_by_sentence` WRITE;
/*!40000 ALTER TABLE `al_test_result_by_sentence` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_test_result_by_sentence` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_test`.`al_test_result_by_sentence_BEFORE_INSERT` BEFORE INSERT ON `al_test_result_by_sentence` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `yj_autolearning_train`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `yj_autolearning_train` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `yj_autolearning_train`;

--
-- Table structure for table `al_train_model_info`
--

DROP TABLE IF EXISTS `al_train_model_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_train_model_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_uuid` varchar(64) NOT NULL,
  `model_url` varchar(255) NOT NULL,
  `model_create_time` int(11) DEFAULT NULL,
  `model_status` smallint(6) NOT NULL DEFAULT '0',
  `train_uuid` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_model_uuid` (`model_uuid`),
  KEY `idx_train_uuid` (`train_uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_train_model_info`
--

LOCK TABLES `al_train_model_info` WRITE;
/*!40000 ALTER TABLE `al_train_model_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_train_model_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_train`.`al_train_model_info_BEFORE_INSERT` BEFORE INSERT ON `al_train_model_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_train_record`
--

DROP TABLE IF EXISTS `al_train_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_train_record` (
  `train_id` varchar(64) NOT NULL,
  `init_model_uuid` varchar(64) DEFAULT NULL,
  `init_model_url` varchar(255) DEFAULT NULL,
  `model_status` int(11) DEFAULT NULL,
  `prepare_id` varchar(64) DEFAULT NULL,
  `corpus_url` varchar(255) DEFAULT NULL,
  `corpus_status` int(11) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `new_model_uuid` varchar(64) DEFAULT NULL,
  `new_model_url` varchar(255) DEFAULT NULL,
  `new_model_time` datetime DEFAULT NULL,
  `train_status` int(11) DEFAULT NULL,
  `test_status` int(11) DEFAULT NULL,
  `model_save_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`train_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_train_record`
--

LOCK TABLES `al_train_record` WRITE;
/*!40000 ALTER TABLE `al_train_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_train_record` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `al_train_request_info`
--

DROP TABLE IF EXISTS `al_train_request_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_train_request_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `train_uuid` varchar(64) NOT NULL,
  `train_start_time` int(11) DEFAULT NULL,
  `train_finish_time` int(11) DEFAULT NULL,
  `train_switch_mode` int(11) NOT NULL DEFAULT '0',
  `train_status` int(11) NOT NULL DEFAULT '0',
  `train_verbose` mediumtext,
  `corpus_uuid` varchar(64) DEFAULT NULL,
  `corpus_dir` varchar(255) DEFAULT NULL,
  `init_model_uuid` varchar(64) DEFAULT NULL,
  `init_model_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_train_uuid` (`train_uuid`),
  KEY `idx_corpus_uuid` (`corpus_uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=1348 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_train_request_info`
--

LOCK TABLES `al_train_request_info` WRITE;
/*!40000 ALTER TABLE `al_train_request_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_train_request_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `yj_autolearning_train`.`al_train_request_info_BEFORE_INSERT` BEFORE INSERT ON `al_train_request_info` FOR EACH ROW
BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `yj_autolearning_web`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `yj_autolearning_web` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `yj_autolearning_web`;

--
-- Table structure for table `al_common_async_req`
--

DROP TABLE IF EXISTS `al_common_async_req`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_common_async_req` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `req_uuid` varchar(64) NOT NULL COMMENT '异步请求的全局ID',
  `req_type` smallint(6) NOT NULL DEFAULT '0',
  `req_create_uid` int(11) DEFAULT NULL COMMENT '请求用户',
  `req_create_time` int(11) DEFAULT NULL COMMENT '请求开始时间',
  `req_finish_time` int(11) DEFAULT NULL COMMENT '请求结束时间',
  `req_status` smallint(6) DEFAULT NULL COMMENT '请求状态：0-未开始,1-进行中,2-成功,3-失败',
  `req_errno` varchar(15) DEFAULT NULL COMMENT '请求错误码',
  `req_errmsg` varchar(1024) DEFAULT NULL COMMENT '请求错误信息',
  `req_result` varchar(5000) DEFAULT NULL COMMENT '请求结果，json',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_common_async_req`
--

LOCK TABLES `al_common_async_req` WRITE;
/*!40000 ALTER TABLE `al_common_async_req` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_common_async_req` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_common_async_req_BEFORE_INSERT` BEFORE INSERT ON `al_common_async_req` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_common_region`
--

DROP TABLE IF EXISTS `al_common_region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_common_region` (
  `insert_time` int(11) DEFAULT NULL COMMENT '数据插入的时间',
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL COMMENT '区域ID',
  `name` varchar(50) NOT NULL COMMENT '区域名称',
  `parent_id` int(11) NOT NULL DEFAULT '0' COMMENT '区域父级ID：无父级为0',
  `level` smallint(6) DEFAULT NULL COMMENT '区域级别：0：省级；1：市级；2：区级',
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`) USING BTREE,
  KEY `idx_name` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='区域表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_common_region`
--

LOCK TABLES `al_common_region` WRITE;
/*!40000 ALTER TABLE `al_common_region` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_common_region` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_common_region_BEFORE_INSERT` BEFORE INSERT ON `al_common_region` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_label_diting_info`
--

DROP TABLE IF EXISTS `al_label_diting_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_label_diting_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL COMMENT '伪删除标识：0-正常，1-已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增长id',
  `start_time` datetime(3) DEFAULT NULL COMMENT 'diting语句识别的开始时间',
  `uuid` varchar(64) NOT NULL COMMENT 'ditting与客户端之间的请求id',
  `request_id` varchar(64) NOT NULL COMMENT 'ditting与asr之间的请求id，即语句id',
  `end_time` datetime(3) DEFAULT NULL COMMENT 'diting语句识别的结束时间',
  `http_cost_time` int(11) DEFAULT NULL COMMENT 'diting到asr的http传输时延，单位：毫秒',
  `trans_delay` int(11) DEFAULT NULL COMMENT '客户端到diting之间的传输时延',
  `related_status` smallint(1) DEFAULT '0' COMMENT '是否已经完成trans_delay的计算，0-未完成；1-已完成',
  `time` datetime(3) DEFAULT NULL COMMENT '从mongodb中获取，该记录的保存时间',
  `line_id` varchar(128) DEFAULT NULL COMMENT '从mongodb中获取，role_id@court_id@case_id',
  `case_id` varchar(64) DEFAULT NULL COMMENT '案件id，从mongodb中获取',
  `court_id` varchar(64) DEFAULT NULL COMMENT '法庭id，从mongodb中获取',
  `role_id` varchar(64) DEFAULT NULL COMMENT '角色id，从mongodb中获取',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_request_id` (`request_id`) USING BTREE COMMENT '语句id'
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_label_diting_info`
--

LOCK TABLES `al_label_diting_info` WRITE;
/*!40000 ALTER TABLE `al_label_diting_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_label_diting_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_label_diting_info_BEFORE_INSERT` BEFORE INSERT ON `al_label_diting_info` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_label_project`
--

DROP TABLE IF EXISTS `al_label_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_label_project` (
  `insert_time` int(11) DEFAULT NULL COMMENT '数据插入的时间',
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proj_code` varchar(24) NOT NULL COMMENT '项目编号：通过程序生成，作为唯一标识',
  `proj_name` varchar(24) NOT NULL COMMENT '项目名称',
  `proj_desc` varchar(2000) DEFAULT NULL COMMENT '项目说明',
  `proj_status` smallint(6) NOT NULL DEFAULT '0' COMMENT '项目状态',
  `create_uid` int(11) NOT NULL COMMENT '项目创建的用户ID：关联al_user表的id',
  `create_time` int(11) DEFAULT NULL COMMENT '标注项目创建的时间',
  `region_id` int(11) NOT NULL COMMENT '项目创建的用户ID：关联al_user表的id',
  `region_full_ids` varchar(100) DEFAULT NULL,
  `region_full_name` varchar(100) DEFAULT NULL,
  `proj_difficulty` decimal(8,3) DEFAULT '1.000',
  PRIMARY KEY (`id`),
  UNIQUE KEY `proj_code` (`proj_code`) USING BTREE,
  KEY `idx_create_time` (`create_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COMMENT='标注项目表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_label_project`
--

LOCK TABLES `al_label_project` WRITE;
/*!40000 ALTER TABLE `al_label_project` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_label_project` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_label_project_BEFORE_INSERT` BEFORE INSERT ON `al_label_project` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_label_result`
--

DROP TABLE IF EXISTS `al_label_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_label_result` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` varchar(50) NOT NULL COMMENT '语句全局ID：关联al_utterance一系列表',
  `uttr_stt_time` int(11) DEFAULT NULL COMMENT '语句识别时间：冗余engine库al_utterance_access.time',
  `uttr_url` varchar(255) DEFAULT NULL COMMENT '语句相对路径：冗余engine库al_utterance.url',
  `uttr_result` varchar(1024) DEFAULT NULL COMMENT '语句识别结果：冗余engine库al_utterance_access.result',
  `proj_id` int(11) DEFAULT NULL COMMENT '项目ID：关联al_label_project表的id',
  `proj_code` varchar(24) DEFAULT NULL COMMENT '项目编号：冗余web库al_label_project.proj_code',
  `proj_name` varchar(24) DEFAULT NULL COMMENT '项目名称：冗余web库al_label_project.proj_name',
  `task_id` int(11) DEFAULT NULL COMMENT '任务ID：关联al_label_task表的id',
  `task_code` varchar(24) DEFAULT NULL COMMENT '项目编号：冗余web库al_label_task.task_code',
  `task_name` varchar(24) DEFAULT NULL COMMENT '项目名称：冗余web库al_label_task.task_name',
  `label_status` int(11) NOT NULL DEFAULT '0' COMMENT '标注状态： 0：未标注, 1：已标注',
  `label_text` varchar(500) DEFAULT NULL COMMENT '标注文本',
  `label_time` int(11) DEFAULT NULL COMMENT '标注时间',
  `label_uid` int(11) DEFAULT NULL COMMENT '实际标注人ID：关联al_sysmgr_user的ID',
  `label_counter` int(11) DEFAULT '0' COMMENT '标注修改次数：需要实际有改动才+1',
  `ins_cnt` int(11) DEFAULT NULL COMMENT '插入数（insertion_count）',
  `sub_cnt` int(11) DEFAULT NULL COMMENT '替换数（substitution_count）',
  `del_cnt` int(11) DEFAULT NULL COMMENT '删除数（deletion_count）',
  `wer` decimal(8,4) DEFAULT NULL COMMENT '错误率（word_error_ratio）',
  `label_tag_person` varchar(255) DEFAULT NULL COMMENT '音频中说话人的名字（或称号）',
  `label_tag_accent` varchar(255) DEFAULT NULL COMMENT '音频中说话人的口音',
  `label_tag_gender` varchar(255) DEFAULT NULL COMMENT '音频中说话人的性别',
  PRIMARY KEY (`id`),
  KEY `idx_request_id` (`request_id`) USING BTREE,
  KEY `idx_proj_id` (`proj_id`) USING BTREE,
  KEY `idx_task_id` (`task_id`) USING BTREE,
  KEY `idx_label_time` (`label_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=635386 DEFAULT CHARSET=utf8mb4 COMMENT='标注结果表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_label_result`
--

LOCK TABLES `al_label_result` WRITE;
/*!40000 ALTER TABLE `al_label_result` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_label_result` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_label_result_BEFORE_INSERT` BEFORE INSERT ON `al_label_result` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_label_task`
--

DROP TABLE IF EXISTS `al_label_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_label_task` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `task_code` varchar(24) NOT NULL COMMENT '任务编号：通过程序生成，作为唯一标识',
  `task_name` varchar(24) NOT NULL COMMENT '任务名称',
  `proj_id` int(11) NOT NULL COMMENT '项目ID：关联al_label_project表的id，不关联值为0',
  `create_uid` int(11) DEFAULT NULL COMMENT '任务创建的用户ID：关联al_sysmgr_user表的id',
  `create_time` int(11) DEFAULT NULL COMMENT '标注任务创建的时间',
  `task_status` smallint(6) NOT NULL DEFAULT '0' COMMENT '任务状态',
  `finish_time` int(11) DEFAULT NULL COMMENT '标注完成时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `task_code_UNIQUE` (`task_code`) USING BTREE,
  KEY `idx_create_time` (`create_time`) USING BTREE,
  KEY `idx_task_name` (`task_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=222 DEFAULT CHARSET=utf8mb4 COMMENT='标注任务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_label_task`
--

LOCK TABLES `al_label_task` WRITE;
/*!40000 ALTER TABLE `al_label_task` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_label_task` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_label_task_BEFORE_INSERT` BEFORE INSERT ON `al_label_task` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_label_user_map`
--

DROP TABLE IF EXISTS `al_label_user_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_label_user_map` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL COMMENT '用户ID：关联al_sysmgr_user表的id',
  `rel_id` int(11) NOT NULL COMMENT '关系ID：\n若rel_type=0，则关联al_label_project表的id；\n若rel_type=1，则关联al_label_task表的id',
  `rel_type` smallint(6) DEFAULT '0' COMMENT '关系类型：\n0：默认值，代替null;\n1：项目关系;\n2：任务关系;',
  PRIMARY KEY (`id`),
  KEY `idx_type_ref_id` (`rel_type`,`rel_id`) USING BTREE,
  KEY `idx_type_uid` (`rel_type`,`uid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=379 DEFAULT CHARSET=utf8mb4 COMMENT='用户与标注项目/任务关系表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_label_user_map`
--

LOCK TABLES `al_label_user_map` WRITE;
/*!40000 ALTER TABLE `al_label_user_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_label_user_map` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_label_user_map_BEFORE_INSERT` BEFORE INSERT ON `al_label_user_map` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_label_utterance_info`
--

DROP TABLE IF EXISTS `al_label_utterance_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_label_utterance_info` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) NOT NULL DEFAULT '0',
  `ng_version` varchar(64) NOT NULL COMMENT '引擎版本号',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_id` varchar(64) NOT NULL COMMENT '语句id',
  `time` datetime NOT NULL COMMENT '语句识别的结束时间',
  `app` varchar(64) DEFAULT NULL,
  `group` varchar(64) DEFAULT NULL,
  `ip` varchar(16) DEFAULT NULL COMMENT '客户端ip',
  `app_key` varchar(64) DEFAULT NULL,
  `session_id` varchar(64) DEFAULT NULL,
  `device_uuid` varchar(64) DEFAULT NULL,
  `uid` varchar(64) DEFAULT NULL,
  `start_timestamp` varchar(13) DEFAULT NULL COMMENT '语句识别的开始时间',
  `latency` int(8) DEFAULT NULL COMMENT '时延',
  `status_code` varchar(16) DEFAULT NULL,
  `status_message` varchar(1024) DEFAULT NULL,
  `backend_apps` varchar(255) DEFAULT NULL,
  `duration` int(8) DEFAULT NULL,
  `audio_format` varchar(32) DEFAULT NULL,
  `audio_url` varchar(255) DEFAULT NULL COMMENT '未知',
  `sample_rate` int(16) DEFAULT NULL COMMENT '采样率，单位：1000',
  `method` varchar(64) DEFAULT NULL,
  `packet_count` int(8) DEFAULT NULL,
  `avg_packet_duration` int(8) DEFAULT NULL,
  `total_rtf` decimal(8,3) DEFAULT NULL,
  `raw_rtf` decimal(8,3) DEFAULT NULL,
  `real_rtf` decimal(8,3) DEFAULT NULL COMMENT '识别速率',
  `detect_duration` int(8) DEFAULT NULL COMMENT '语句时长',
  `total_cost_time` int(8) DEFAULT NULL,
  `receive_cost_time` int(8) DEFAULT NULL,
  `wait_cost_time` int(8) DEFAULT NULL,
  `process_time` int(8) DEFAULT NULL,
  `processor_id` int(8) DEFAULT NULL,
  `user_id` varchar(64) DEFAULT NULL,
  `vocabulary_id` varchar(64) DEFAULT NULL,
  `keyword_list_id` varchar(64) DEFAULT NULL,
  `customization_id` varchar(64) DEFAULT NULL,
  `class_vocabulary_id` varchar(64) DEFAULT NULL,
  `result` varchar(1024) NOT NULL COMMENT '识别结果',
  `group_name` varchar(64) DEFAULT NULL,
  `path` varchar(255) NOT NULL COMMENT '语句音频文件原始的',
  `url` varchar(255) NOT NULL COMMENT '语句音频文件的url',
  `truncation_ratio` decimal(8,4) DEFAULT NULL COMMENT '语句音频文件的截幅比',
  `volume` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的音量',
  `snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的信噪比',
  `pre_snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的前信噪比',
  `post_snr` decimal(8,2) DEFAULT NULL COMMENT '语句音频文件的后信噪比',
  `is_assigned` smallint(6) NOT NULL DEFAULT '0',
  `uttr_status` smallint(6) NOT NULL DEFAULT '0',
  `prepare_uuid` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_request_id` (`request_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=681917 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_label_utterance_info`
--

LOCK TABLES `al_label_utterance_info` WRITE;
/*!40000 ALTER TABLE `al_label_utterance_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_label_utterance_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_label_utterance_info_BEFORE_INSERT` BEFORE INSERT ON `al_label_utterance_info` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_sysmgr_permission`
--

DROP TABLE IF EXISTS `al_sysmgr_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_sysmgr_permission` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '权限ID',
  `pname` varchar(24) NOT NULL COMMENT '权限名称',
  `pcategory` smallint(6) DEFAULT NULL COMMENT '权限范畴（暂不用）',
  `ptype` smallint(6) DEFAULT NULL COMMENT '权限范畴下的分类（暂不用）',
  `presource` varchar(200) DEFAULT NULL COMMENT '权限资源uri',
  `create_time` int(11) DEFAULT NULL COMMENT '权限创建的时间',
  PRIMARY KEY (`id`),
  KEY `idx_create_time` (`create_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_sysmgr_permission`
--

LOCK TABLES `al_sysmgr_permission` WRITE;
/*!40000 ALTER TABLE `al_sysmgr_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_sysmgr_permission` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_sysmgr_permission_BEFORE_INSERT` BEFORE INSERT ON `al_sysmgr_permission` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_sysmgr_role`
--

DROP TABLE IF EXISTS `al_sysmgr_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_sysmgr_role` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `rname` varchar(24) NOT NULL COMMENT '角色名称',
  `rcode` varchar(24) DEFAULT NULL COMMENT '角色编码',
  `rdesc` varchar(200) DEFAULT '' COMMENT '角色说明',
  `create_time` int(11) DEFAULT NULL COMMENT '角色创建的时间',
  `rgroup` smallint(6) DEFAULT '-1',
  `rlevel` smallint(6) DEFAULT '100',
  PRIMARY KEY (`id`),
  KEY `idx_rcode` (`rcode`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COMMENT='角色表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_sysmgr_role`
--

LOCK TABLES `al_sysmgr_role` WRITE;
/*!40000 ALTER TABLE `al_sysmgr_role` DISABLE KEYS */;
INSERT INTO `al_sysmgr_role` VALUES (1572860023,0,1,'超级管理员','superadmin','超级管理员，拥有该系统的所有权限',1561625390,0,0),(1572860023,0,2,'项目管理员','projmanager','项目管理员用于管理项目，可管理多个项目',1561625394,1,10),(1572860023,0,3,'任务管理员','taskmanager','任务管理员用于管理任务，用于任务的创建、分配和审核',1561625394,1,20),(1572860023,0,4,'标注人员','taskoperator','标注人员用于执行标注任务',1561625394,1,100),(1572860023,0,5,'运维人员','supervisor','通用运维人员，主要职责是监控引擎识别的情况。',1561626344,2,10);
/*!40000 ALTER TABLE `al_sysmgr_role` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_sysmgr_role_BEFORE_INSERT` BEFORE INSERT ON `al_sysmgr_role` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_sysmgr_rp_map`
--

DROP TABLE IF EXISTS `al_sysmgr_rp_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_sysmgr_rp_map` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rid` int(11) NOT NULL COMMENT '角色ID（role_id)：关联al_sysmgr_role表的id',
  `pid` int(11) NOT NULL COMMENT '权限ID（permission_id)：关联al_sysmgr_permission表的id',
  PRIMARY KEY (`id`),
  KEY `idx_rid` (`rid`) USING BTREE,
  KEY `idx_pid` (`pid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关系表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_sysmgr_rp_map`
--

LOCK TABLES `al_sysmgr_rp_map` WRITE;
/*!40000 ALTER TABLE `al_sysmgr_rp_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `al_sysmgr_rp_map` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_sysmgr_rp_map_BEFORE_INSERT` BEFORE INSERT ON `al_sysmgr_rp_map` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `al_sysmgr_user`
--

DROP TABLE IF EXISTS `al_sysmgr_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `al_sysmgr_user` (
  `insert_time` int(11) DEFAULT NULL,
  `is_deleted` smallint(6) DEFAULT '0' COMMENT '伪删除标识：\n0：正常，1：已删除',
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `account` varchar(24) NOT NULL COMMENT '用户账号',
  `password` varchar(100) DEFAULT NULL COMMENT '账号密码：\n现用flask的默认加密方式pbkdf2:sha256',
  `nickname` varchar(24) NOT NULL COMMENT '用户昵称',
  `telephone` varchar(15) DEFAULT NULL COMMENT '联系电话',
  `ac_type` smallint(6) DEFAULT '0' COMMENT '账号类型（account_type）：用于区分账号登录方式。\n100：web页面登陆形式',
  `ac_status` smallint(6) DEFAULT '0' COMMENT '账号状态（account_status）：预留用于账号冻结激活等管理功能\n1：超级管理员，不可以通过页面修改；\n11：用户正常状态；',
  `create_time` int(11) DEFAULT NULL COMMENT '用户创建的时间',
  `rid` int(11) DEFAULT NULL COMMENT '角色ID（role_id)：关联al_role表的id',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_account` (`account`) USING BTREE,
  KEY `idx_create_time` (`create_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `al_sysmgr_user`
--

LOCK TABLES `al_sysmgr_user` WRITE;
/*!40000 ALTER TABLE `al_sysmgr_user` DISABLE KEYS */;
INSERT INTO `al_sysmgr_user` VALUES (1572860023,0,1,'superadmin','pbkdf2:sha256:150000$gk7UloUv$8f34dcde831f1d30afa51e7703165bc5fca1ccc506d81adc34f5e58563c478fb','超级管理员','',100,1,1572860023,1),(1578383485,0,118,'happy','pbkdf2:sha256:150000$LepQpJsY$a38db35363d9e1f9b4c358de9d018f673744ddfe2a9fd856aec376e899eca7b2','superadmin',NULL,100,11,1578383485,1);
/*!40000 ALTER TABLE `al_sysmgr_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`192.168.%`*/ /*!50003 TRIGGER `oll_sysmgr_user_BEFORE_INSERT` BEFORE INSERT ON `al_sysmgr_user` FOR EACH ROW BEGIN
	IF NEW.insert_time IS NULL THEN 
		SET NEW.insert_time = unix_timestamp(CURRENT_TIMESTAMP);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-01-07 16:32:40
