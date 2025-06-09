-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: test1
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_logs`
--

DROP TABLE IF EXISTS `activity_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_logs` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `organization_id` int DEFAULT NULL,
  `login_time` datetime DEFAULT NULL,
  `logout_time` datetime DEFAULT NULL,
  `service_accessed` varchar(100) DEFAULT NULL,
  `provider_organization_id` int DEFAULT NULL,
  `details` text,
  PRIMARY KEY (`log_id`),
  KEY `user_id` (`user_id`),
  KEY `organization_id` (`organization_id`),
  KEY `provider_organization_id` (`provider_organization_id`),
  CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `activity_logs_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`),
  CONSTRAINT `activity_logs_ibfk_3` FOREIGN KEY (`provider_organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_logs`
--

LOCK TABLES `activity_logs` WRITE;
/*!40000 ALTER TABLE `activity_logs` DISABLE KEYS */;
INSERT INTO `activity_logs` VALUES (1,3,NULL,'2025-05-05 07:54:06',NULL,NULL,NULL,NULL),(2,2,NULL,'2025-05-05 07:54:34',NULL,NULL,NULL,NULL),(3,3,NULL,'2025-05-05 08:02:58',NULL,NULL,NULL,NULL),(4,4,1,'2025-05-05 08:03:17',NULL,NULL,NULL,NULL),(5,2,NULL,'2025-05-05 08:22:02',NULL,NULL,NULL,NULL),(6,3,NULL,'2025-05-05 08:22:54',NULL,NULL,NULL,NULL),(7,5,2,'2025-05-05 08:23:18','2025-05-05 08:24:44',NULL,NULL,NULL),(8,4,1,'2025-05-05 08:25:02','2025-05-05 08:26:34',NULL,NULL,NULL),(9,5,2,'2025-05-05 08:26:50',NULL,'organization_courses: UIC',1,NULL),(10,7,2,'2025-05-05 08:30:55',NULL,'view_organization: og2',2,NULL),(11,5,2,'2025-05-05 08:31:49','2025-05-05 08:32:34',NULL,NULL,NULL),(12,4,1,'2025-05-05 08:32:48','2025-05-05 08:33:04',NULL,NULL,NULL),(13,7,2,'2025-05-05 08:33:27',NULL,'view_organization: UIC',1,NULL),(14,5,2,'2025-05-05 12:17:35','2025-05-05 12:18:51',NULL,NULL,NULL),(15,4,1,'2025-05-05 12:19:20',NULL,NULL,NULL,NULL),(16,4,1,'2025-05-05 13:46:38',NULL,NULL,NULL,NULL),(17,4,1,'2025-05-05 14:07:58',NULL,NULL,NULL,NULL),(18,4,1,'2025-05-05 14:10:51',NULL,NULL,NULL,NULL),(19,4,1,'2025-05-05 15:06:28',NULL,NULL,NULL,NULL),(20,5,2,'2025-05-05 15:07:01',NULL,NULL,NULL,NULL),(21,5,2,'2025-05-05 16:06:41',NULL,NULL,NULL,NULL),(22,4,1,'2025-05-05 16:12:24',NULL,NULL,NULL,NULL),(25,5,2,'2025-05-05 16:17:15',NULL,NULL,NULL,NULL),(26,7,2,'2025-05-05 16:17:41','2025-05-05 16:23:37','view_organization: UIC',1,NULL),(27,4,1,'2025-05-05 16:23:55','2025-05-05 16:36:15','view_organization: UIC',1,NULL),(29,4,1,'2025-05-05 16:50:19',NULL,'view_organization: og2',2,NULL),(31,4,1,'2025-05-05 17:01:49',NULL,NULL,NULL,NULL),(32,7,2,'2025-05-05 17:02:47',NULL,'organization_courses: og2',2,NULL),(37,4,1,'2025-05-05 17:23:42',NULL,'view_organization: UIC',1,NULL),(38,4,1,'2025-05-05 17:41:45',NULL,NULL,NULL,NULL),(39,5,2,'2025-05-05 17:42:14',NULL,NULL,NULL,NULL),(40,4,1,'2025-05-05 17:51:48',NULL,NULL,NULL,NULL),(42,4,1,'2025-05-05 18:15:17',NULL,'course_search: ',NULL,NULL),(45,4,1,'2025-05-05 18:26:23',NULL,NULL,NULL,NULL),(46,4,1,'2025-05-05 18:28:20',NULL,NULL,NULL,NULL),(48,5,2,'2025-05-05 18:29:57',NULL,NULL,NULL,NULL),(49,7,2,'2025-05-05 18:31:23',NULL,'view_organization: og2',2,NULL),(52,4,1,'2025-05-06 01:27:21','2025-05-06 01:27:47',NULL,NULL,NULL),(54,4,1,'2025-05-06 01:34:51',NULL,NULL,NULL,NULL),(56,4,1,'2025-05-06 01:41:08','2025-05-06 01:41:50',NULL,NULL,NULL),(59,4,1,'2025-05-06 04:25:15',NULL,NULL,NULL,NULL),(61,4,1,'2025-05-06 04:34:53','2025-05-06 04:35:07',NULL,NULL,NULL),(63,4,1,'2025-05-06 04:37:07',NULL,NULL,NULL,NULL),(66,4,1,'2025-05-06 05:40:25',NULL,NULL,NULL,NULL),(79,7,2,'2025-05-09 03:39:52',NULL,'view_organization: UIC',1,NULL),(81,4,1,'2025-05-09 04:56:22','2025-05-09 05:03:26',NULL,NULL,NULL),(82,7,2,'2025-05-09 05:03:42',NULL,'thesis_search: UIC论文 - 关键词: AI',1,NULL),(83,4,1,'2025-05-09 05:04:22','2025-05-09 05:18:26',NULL,NULL,NULL),(84,5,2,'2025-05-09 05:18:52','2025-05-09 05:44:28',NULL,NULL,NULL),(85,7,2,'2025-05-09 05:45:01','2025-05-09 06:14:02','thesis_view: UIC论文 - Blockchain Applications in University Records',1,NULL),(87,7,2,'2025-05-15 12:26:14','2025-05-15 12:46:12','view_organization: UIC',1,NULL),(88,5,2,'2025-05-15 12:45:19',NULL,NULL,NULL,NULL),(90,5,2,'2025-05-15 14:11:13','2025-05-15 14:11:20',NULL,NULL,NULL),(91,7,2,'2025-05-15 14:11:42',NULL,'view_organization: UIC',1,NULL),(92,7,2,'2025-05-16 07:02:07',NULL,'view_organization: UIC',1,NULL),(93,7,2,'2025-05-16 07:07:47',NULL,'view_organization: UIC',1,NULL),(94,7,2,'2025-05-16 08:03:19','2025-05-16 08:57:39','view_organization: UIC',1,NULL),(95,7,2,'2025-05-16 08:22:07','2025-05-16 08:28:49','view_organization: UIC',1,NULL),(96,4,1,'2025-05-16 08:29:01','2025-05-16 08:29:10',NULL,NULL,NULL),(98,7,2,'2025-05-16 08:59:02',NULL,'student_auth: UIC学生 - 学生: Alice Huang (ID: S20230001)',1,NULL),(99,7,2,'2025-05-16 09:36:13',NULL,'student_auth: UIC学生 - 学生: Grace Liu (ID: S20230007)',1,NULL),(100,7,2,'2025-05-16 09:51:11',NULL,'view_organization: UIC',1,NULL),(101,2,NULL,'2025-05-16 10:55:50',NULL,NULL,NULL,NULL),(102,7,2,'2025-05-16 10:59:00','2025-05-16 11:35:49','view_organization: UIC',1,NULL),(103,4,1,'2025-05-16 11:36:04','2025-05-16 11:36:20',NULL,NULL,NULL),(105,7,2,'2025-05-16 12:30:09',NULL,'view_organization: UIC',1,NULL),(107,7,2,'2025-05-17 09:06:34',NULL,'view_organization: UIC',1,NULL),(108,7,2,'2025-05-17 09:47:23','2025-05-17 10:09:53','view_organization: UIC',1,NULL),(109,4,1,'2025-05-17 10:10:13','2025-05-17 10:18:57',NULL,NULL,NULL),(111,2,NULL,'2025-05-17 10:38:46',NULL,NULL,NULL,NULL),(112,2,3,'2025-05-17 10:40:29',NULL,'bank_account_setup',NULL,NULL),(113,4,1,'2025-05-17 10:41:07','2025-05-17 11:04:22','organization_courses: UIC',1,NULL),(114,2,3,'2025-05-17 10:42:18',NULL,'bank_account_update',NULL,NULL),(115,4,1,'2025-05-17 11:04:35',NULL,NULL,NULL,NULL),(116,2,NULL,'2025-05-17 11:19:28',NULL,NULL,NULL,NULL),(117,5,2,'2025-05-17 11:43:44',NULL,NULL,NULL,NULL),(118,4,1,'2025-05-17 14:13:31','2025-05-17 15:02:43',NULL,NULL,'常规登录'),(119,21,1,'2025-05-17 15:06:17',NULL,'view_organization: UIC',1,'通过通配符邮箱规则登录'),(120,5,2,'2025-05-17 16:32:42','2025-05-17 16:38:45',NULL,NULL,'常规登录'),(121,24,2,'2025-05-17 16:36:49','2025-05-17 16:37:28','organization_courses: SYSTEM',3,'通过通配符 *@public.hku.com 自动创建用户，访问级别: 1'),(122,24,2,'2025-05-17 16:36:49',NULL,NULL,NULL,'通过通配符邮箱规则登录'),(123,25,2,'2025-05-17 16:37:49','2025-05-17 16:53:39','view_organization: UIC',1,'通过通配符 *@public.hku.com 自动创建用户，访问级别: 1'),(124,25,2,'2025-05-17 16:37:49',NULL,NULL,NULL,'通过通配符邮箱规则登录'),(125,22,2,'2025-05-17 16:38:53','2025-05-17 16:39:06','view_organization: UIC',1,'常规登录'),(126,24,2,'2025-05-17 16:39:27','2025-05-17 16:39:32','view_organization: UIC',1,'通过通配符邮箱规则登录'),(127,24,2,'2025-05-17 16:54:05','2025-05-17 17:03:48','view_organization: SYSTEM',3,'通过通配符邮箱规则登录'),(128,8,NULL,'2025-05-17 17:04:00','2025-05-17 17:05:06','view_organization: og2',2,'常规登录'),(129,2,NULL,'2025-05-17 17:05:24','2025-05-17 17:06:03',NULL,NULL,'常规登录'),(130,4,1,'2025-05-17 17:06:17','2025-05-17 17:10:06',NULL,NULL,'常规登录'),(131,2,NULL,'2025-05-17 17:10:26','2025-05-17 17:14:43',NULL,NULL,'常规登录'),(132,2,NULL,'2025-05-17 17:17:20','2025-05-17 17:21:41',NULL,NULL,'常规登录'),(133,4,1,'2025-05-17 17:21:58',NULL,NULL,NULL,'常规登录'),(134,8,NULL,'2025-05-17 17:40:34','2025-05-17 17:47:11','thesis_search: UIC论文 - 关键词: AI',1,'常规登录'),(135,7,2,'2025-05-17 17:47:50','2025-05-17 18:23:49','thesis_download: UIC论文 - AI in Education and Learning Systems',1,'常规登录'),(136,4,1,'2025-05-17 18:24:07','2025-05-17 18:27:30',NULL,NULL,'常规登录'),(137,7,2,'2025-05-17 18:28:20',NULL,'thesis_view: UIC论文 - AI in Education and Learning Systems',1,'常规登录'),(138,2,NULL,'2025-05-18 16:32:01','2025-05-18 16:32:20',NULL,NULL,'Regular login'),(139,3,NULL,'2025-05-18 16:32:37','2025-05-18 16:33:09',NULL,NULL,'Regular login'),(140,29,4,'2025-05-18 16:33:31','2025-05-18 16:36:28',NULL,NULL,'Regular login'),(141,30,4,'2025-05-18 16:36:56','2025-05-18 16:42:35',NULL,NULL,'Regular login'),(142,30,4,'2025-05-18 16:43:06','2025-05-18 16:44:34',NULL,NULL,'Regular login'),(143,29,4,'2025-05-18 16:45:02','2025-05-18 16:45:22',NULL,NULL,'Regular login'),(144,9,1,'2025-05-18 16:45:47',NULL,'student_auth_batch: MIT student identity - batch verification 6 records',4,'Regular login'),(145,29,4,'2025-05-19 01:00:45','2025-05-19 01:17:42',NULL,NULL,'Regular login'),(146,30,4,'2025-05-19 01:18:05','2025-05-19 01:18:50',NULL,NULL,'Regular login'),(147,9,1,'2025-05-19 01:19:13',NULL,'student_record_batch: MIT student GPA Record - batch query of 6 records',4,'Regular login'),(148,9,1,'2025-05-19 09:00:53','2025-05-19 09:28:03','view_organization: MIT',4,'Regular login'),(149,4,1,'2025-05-19 09:28:22','2025-05-19 09:58:04',NULL,NULL,'Regular login'),(150,9,1,'2025-05-19 09:58:16',NULL,'view_organization: UIC',1,'Regular login'),(151,4,1,'2025-05-19 10:02:17',NULL,NULL,NULL,'Regular login'),(152,9,1,'2025-05-19 10:32:49','2025-05-19 11:02:48','student_record_result: MIT student GPA Record - Student: Alice Huang (ID: S20230001)',4,'Regular login'),(153,1,NULL,'2025-05-19 11:03:42',NULL,NULL,NULL,'Regular login'),(154,1,NULL,'2025-05-19 11:05:10','2025-05-19 11:14:04',NULL,NULL,'Regular login'),(155,9,1,'2025-05-19 11:14:24',NULL,NULL,NULL,'Regular login'),(156,2,NULL,'2025-05-20 02:56:49','2025-05-20 02:57:23',NULL,NULL,'Regular login'),(157,2,NULL,'2025-05-20 03:03:52','2025-05-20 03:04:23',NULL,NULL,'Regular login'),(158,2,NULL,'2025-05-20 03:05:47','2025-05-20 03:06:03',NULL,NULL,'Regular login'),(159,3,NULL,'2025-05-20 03:06:20','2025-05-20 03:06:45',NULL,NULL,'Regular login'),(160,34,7,'2025-05-20 03:07:02','2025-05-20 03:58:23','view_organization: IC',7,'Regular login'),(161,2,NULL,'2025-05-20 03:14:28','2025-05-20 03:15:37',NULL,NULL,'Regular login'),(162,2,NULL,'2025-05-20 03:15:52',NULL,NULL,NULL,'Regular login'),(164,2,3,'2025-05-20 03:23:39','2025-05-20 03:23:52','bank_account_setup',NULL,NULL),(165,2,NULL,'2025-05-20 03:24:08',NULL,NULL,NULL,'Regular login'),(166,2,3,'2025-05-20 03:24:32','2025-05-20 03:41:27','bank_account_update',NULL,NULL),(167,2,NULL,'2025-05-20 03:41:55','2025-05-20 03:43:09',NULL,NULL,'Regular login'),(168,38,7,'2025-05-20 03:48:08',NULL,'view_organization: IC',7,'Regular login'),(169,36,7,'2025-05-20 03:59:46','2025-05-20 04:01:47','view_organization: IC',7,'Regular login'),(170,2,NULL,'2025-05-20 04:02:21','2025-05-20 04:02:32',NULL,NULL,'Regular login'),(171,1,NULL,'2025-05-20 04:03:39','2025-05-20 04:04:03',NULL,NULL,'Regular login'),(172,41,NULL,'2025-05-20 04:04:19','2025-05-20 04:04:28',NULL,NULL,'Regular login'),(173,1,NULL,'2025-05-20 04:04:56','2025-05-20 04:05:09',NULL,NULL,'Regular login'),(174,42,NULL,'2025-05-20 04:05:26','2025-05-20 04:08:32',NULL,NULL,'Regular login'),(175,36,7,'2025-05-20 04:09:49','2025-05-20 04:13:31',NULL,NULL,'Regular login'),(176,4,1,'2025-05-20 04:13:46','2025-05-20 04:13:59',NULL,NULL,'Regular login'),(177,9,1,'2025-05-20 04:14:17','2025-05-20 04:18:57',NULL,NULL,'Regular login'),(178,36,7,'2025-05-20 04:19:27','2025-05-20 04:48:52','view_organization: IC',7,'Regular login'),(179,34,7,'2025-05-20 04:23:50',NULL,NULL,NULL,'Regular login'),(180,43,7,'2025-05-20 07:03:54',NULL,'user_creation_via_wildcard',NULL,'User automatically created via wildcard *@public.ic.com, access level: 1'),(181,43,7,'2025-05-20 07:04:28','2025-05-20 07:04:33',NULL,NULL,'Login via wildcard email rule'),(182,44,7,'2025-05-20 07:05:56','2025-05-20 07:06:26','user_creation_via_wildcard',NULL,'User automatically created via wildcard *@public.ic.com, access level: 1'),(183,44,7,'2025-05-20 07:05:56',NULL,NULL,NULL,'Login via wildcard email rule'),(184,45,7,'2025-05-20 07:07:10','2025-05-20 07:07:40','user_creation_via_wildcard',NULL,'User automatically created via wildcard *@public.ic.com, access level: 1'),(185,45,7,'2025-05-20 07:07:10',NULL,NULL,NULL,'Login via wildcard email rule'),(186,46,7,'2025-05-20 07:08:24','2025-05-20 07:31:44','thesis_search: IC thesis - Keyword: AI',7,'User automatically created via wildcard *@public.ic.com, access level: 1'),(187,46,7,'2025-05-20 07:08:24',NULL,NULL,NULL,'Login via wildcard email rule'),(188,1,NULL,'2025-05-20 07:10:38','2025-05-20 07:12:39',NULL,NULL,'Regular login'),(189,34,7,'2025-05-20 07:13:20','2025-05-20 07:47:43',NULL,NULL,'Regular login'),(190,16,2,'2025-05-20 07:32:02','2025-05-20 07:32:45','thesis_search: UIC thesis - Keyword: AI',1,'Regular login'),(191,34,7,'2025-05-20 07:33:03','2025-05-20 07:34:34',NULL,NULL,'Regular login'),(192,47,7,'2025-05-20 07:34:48','2025-05-20 07:35:45','view_organization: IC',7,'Regular login'),(193,34,7,'2025-05-20 07:36:48','2025-05-20 07:37:49',NULL,NULL,'Regular login'),(194,9,1,'2025-05-20 07:38:14','2025-05-20 07:44:39','thesis_search: IC thesis - Keyword: AI',7,'Regular login'),(195,40,7,'2025-05-20 07:44:57','2025-05-20 07:45:36','view_organization: IC',7,'Regular login'),(196,34,7,'2025-05-20 07:45:51','2025-05-20 07:46:56',NULL,NULL,'Regular login'),(197,8,NULL,'2025-05-20 07:47:28','2025-05-20 07:55:03','view_organization: IC',7,'Regular login'),(198,4,1,'2025-05-20 07:47:57','2025-05-20 08:01:21',NULL,NULL,'Regular login'),(199,9,1,'2025-05-20 07:55:24','2025-05-20 08:06:38','view_organization: IC',7,'Regular login'),(200,36,7,'2025-05-20 08:02:08','2025-05-20 08:07:32','view_organization: IC',7,'Regular login'),(201,15,1,'2025-05-20 08:06:55',NULL,'organization_courses: IC',7,'Regular login'),(202,34,7,'2025-05-20 08:07:46','2025-05-20 08:08:42',NULL,NULL,'Regular login'),(203,4,1,'2025-05-20 08:09:00',NULL,NULL,NULL,'Regular login');
/*!40000 ALTER TABLE `activity_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `api_configs`
--

DROP TABLE IF EXISTS `api_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `api_configs` (
  `config_id` int NOT NULL AUTO_INCREMENT,
  `service_id` int NOT NULL,
  `base_url` varchar(255) NOT NULL,
  `path` varchar(255) NOT NULL,
  `method` varchar(10) NOT NULL,
  `input` json DEFAULT NULL,
  `output` json DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `config_name` varchar(100) NOT NULL DEFAULT '默认配置',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`config_id`),
  KEY `api_configs_ibfk_1` (`service_id`),
  CONSTRAINT `api_configs_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `api_configs`
--

LOCK TABLES `api_configs` WRITE;
/*!40000 ALTER TABLE `api_configs` DISABLE KEYS */;
INSERT INTO `api_configs` VALUES (1,6,'http://172.16.160.88:8001','/hw/thesis/search','POST','{\"keywords\": \"string\"}','{\"title\": \"string\", \"abstract\": \"string\"}','2025-05-05 17:07:07','2025-05-16 08:31:26','默认配置',1),(4,6,'http://172.16.160.88:8001','/hw/thesis/pdf','POST','{\"title\": \"string\"}','{\"response\": {\"type\": \"file\", \"format\": \"pdf\"}}','2025-05-06 03:51:42','2025-05-16 08:31:32','论文pdf',1),(5,5,'http://172.16.160.88:8001','/hw/student/authenticate','POST','{\"id\": \"string\", \"name\": \"string\"}','{\"status\": \"string\"}','2025-05-06 05:41:48','2025-05-16 11:38:58','UIC学生',1),(6,8,'http://172.16.160.88:8001','/hw/student/record','POST','{\"id\": \"string\", \"name\": \"string\"}','{\"gpa\": 0, \"name\": \"string\", \"enroll_year\": \"string\", \"graduation_year\": \"string\"}','2025-05-09 04:57:40','2025-05-16 08:30:16','UIC学生GPA Record',1),(7,11,'http://172.16.160.88:8001','/hw/student/authenticate','POST','{\"id\": \"string\", \"name\": \"string\"}','{\"status\": \"string\"}','2025-05-18 16:38:25',NULL,'student identity config',1),(8,12,'http://172.16.160.88:8001','/hw/thesis/search','POST','{\"keywords\": \"string\"}','{\"title\": \"string\", \"abstract\": \"string\"}','2025-05-18 16:39:05',NULL,'thesis config',1),(9,12,'http://172.16.160.88:8001','/hw/thesis/pdf','POST','{\"title\": \"string\"}','{\"response\": {\"type\": \"file\", \"format\": \"pdf\"}}','2025-05-18 16:39:42',NULL,'thesis pdf config',1),(10,13,'http://172.16.160.88:8001','/hw/student/record','POST','{\"id\": \"string\", \"name\": \"string\"}','{\"gpa\": 0, \"name\": \"string\", \"enroll_year\": \"string\", \"graduation_year\": \"string\"}','2025-05-19 01:18:43',NULL,'GPA Record config',1),(11,16,'http://172.16.160.88:8001','/hw/student/authenticate','POST','{\"id\": \"string\", \"name\": \"string\"}','{\"status\": \"string\"}','2025-05-20 04:20:48',NULL,'IC identity student',1),(12,15,'http://172.16.160.88:8001','/hw/thesis/search','POST','{\"keywords\": \"string\"}','{\"title\": \"string\", \"abstract\": \"string\"}','2025-05-20 04:22:13',NULL,' ic_thesis_search',1),(13,15,'http://172.16.160.88:8001','/hw/thesis/pdf','POST','{\"title\": \"string\"}','{\"response\": {\"type\": \"file\", \"format\": \"pdf\"}}','2025-05-20 04:22:55',NULL,'thesis_pdf',1),(15,17,'http://172.16.160.88:8001','/hw/student/record','POST','{\"id\": \"string\", \"name\": \"string\"}','{\"gpa\": 0, \"name\": \"string\", \"enroll_year\": \"string\", \"graduation_year\": \"string\"}','2025-05-20 04:38:08','2025-05-20 08:02:54','IC_STUDENT_GPA Record',1);
/*!40000 ALTER TABLE `api_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bank_accounts`
--

DROP TABLE IF EXISTS `bank_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bank_accounts` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `bank_name` varchar(100) NOT NULL,
  `account_name` varchar(100) NOT NULL,
  `account_no` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `is_system_account` tinyint(1) NOT NULL DEFAULT '0',
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE KEY `organization_id` (`organization_id`),
  CONSTRAINT `bank_accounts_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bank_accounts`
--

LOCK TABLES `bank_accounts` WRITE;
/*!40000 ALTER TABLE `bank_accounts` DISABLE KEYS */;
INSERT INTO `bank_accounts` VALUES (1,2,'Bank of Utopia','EdGrow Finance Co.','393077718917153','2025-05-05 08:29:30','2025-05-09 05:19:40',0,'9217'),(2,1,'FutureLearn Federal Bank','Utopia Credit Union','670547811218584','2025-05-09 05:05:07','2025-05-19 10:02:31',0,'9978'),(4,4,'Global Education Bank','EdGrow Finance Co.','137070703603485','2025-05-18 16:34:04',NULL,0,'1851'),(5,3,'E-DBA Bank','E-DBA account','596117071864958','2025-05-20 03:23:39','2025-05-20 03:24:32',1,NULL),(6,7,'Bank of Utopia','Scholars Advantage Trust','281045870632903','2025-05-20 03:32:40',NULL,0,'9802');
/*!40000 ALTER TABLE `bank_accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `title` varchar(200) NOT NULL,
  `units` float NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,2,'C programming',3,'aaaa','2025-05-05 18:32:03',NULL),(2,4,'Python',3,'this a good course for python beginner','2025-05-18 16:43:49',NULL),(3,4,'software engineering',3,'you can learn how to develop a software.','2025-05-18 16:44:24',NULL),(4,7,'C programming',2,'this is C programming.','2025-05-20 04:10:17','2025-05-20 04:10:54');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `help_requests`
--

DROP TABLE IF EXISTS `help_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `help_requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text NOT NULL,
  `is_answered` tinyint(1) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `response` text,
  `submit_time` datetime DEFAULT NULL,
  `response_time` datetime DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `help_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `help_requests`
--

LOCK TABLES `help_requests` WRITE;
/*!40000 ALTER TABLE `help_requests` DISABLE KEYS */;
INSERT INTO `help_requests` VALUES (1,8,'Python','abcdefgaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',1,0,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa','2025-05-05 17:12:22','2025-05-05 17:13:19'),(2,2,'question1','I have question.',1,0,'ok. I answer your question','2025-05-17 17:14:35','2025-05-17 17:16:54'),(3,9,'question of quota','why i dont have enough quota for \"thesis downloa\"?',1,0,'Quota is set by your organization convener, connect her to learn more detail.','2025-05-19 11:16:26','2025-05-19 11:18:50'),(4,46,'Network question','I have question about network.',1,0,'okok','2025-05-20 07:09:55','2025-05-20 07:10:56');
/*!40000 ALTER TABLE `help_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members` (
  `member_id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(120) NOT NULL,
  `access_level` int NOT NULL,
  `quota` float DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`member_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `members_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
INSERT INTO `members` VALUES (2,2,'cyj','cyj@gmail.com',3,100,'2025-05-05 08:29:48'),(4,1,'zl','zl@uic.com',2,40,'2025-05-17 10:10:29'),(5,1,'tyy','tyy@uic.com',3,0,'2025-05-17 10:10:43'),(6,1,'cyj','cyj@uic.com',2,0,'2025-05-17 10:41:25'),(9,1,'lelezhou','lelezhou@uic.com',1,1000,'2025-05-17 10:48:43'),(10,1,'aaa','aaa@uic.com',1,0,'2025-05-17 11:05:08'),(11,2,'aaa','aaa@gmail.com',3,0,'2025-05-17 11:44:13'),(25,1,'张三','zhangsan@example.com',1,0,'2025-05-17 15:02:14'),(27,1,'通配符用户(example.com域)','*@example.com',3,500,'2025-05-17 15:02:14'),(28,2,'张三','zhangsan@gmail.com',2,0,'2025-05-17 16:35:07'),(29,2,'李四','lisi@gmail.com',3,100,'2025-05-17 16:35:07'),(30,2,'通配符用户(public.hku.com域)','*@public.hku.com',1,500,'2025-05-17 16:35:07'),(37,4,'mitprovider','mitprovider@mit.com',3,50,'2025-05-18 16:34:27'),(38,7,'chen','chen@ic.com',3,30,'2025-05-20 03:35:00'),(39,7,'joyce','joyce@ic.com',3,0,'2025-05-20 03:35:48'),(41,7,'zeo','zeo@ic.com',2,20,'2025-05-20 03:35:48'),(42,7,'lily','lily@ic.com',3,60,'2025-05-20 03:35:48'),(43,7,'lele','lele@ic.com',2,80,'2025-05-20 03:35:48'),(44,7,'Wildcard User (public.ic.com domain)','*@public.ic.com',1,0,'2025-05-20 03:35:48'),(45,7,'neo','neo@ic.com',1,10,'2025-05-20 07:34:26');
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `membership_fees`
--

DROP TABLE IF EXISTS `membership_fees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_fees` (
  `fee_id` int NOT NULL AUTO_INCREMENT,
  `access_level` int NOT NULL,
  `fee_type` varchar(20) NOT NULL,
  `fee_amount` float NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`fee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership_fees`
--

LOCK TABLES `membership_fees` WRITE;
/*!40000 ALTER TABLE `membership_fees` DISABLE KEYS */;
INSERT INTO `membership_fees` VALUES (1,1,'flat_rate',1000,'2025-05-05 07:52:47','2025-05-20 03:16:14'),(2,2,'per_person',20,'2025-05-05 07:52:47','2025-05-17 11:43:23'),(3,3,'per_person',100000000000000,'2025-05-05 07:52:47','2025-05-20 03:42:10');
/*!40000 ALTER TABLE `membership_fees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organizations`
--

DROP TABLE IF EXISTS `organizations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organizations` (
  `organization_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(200) NOT NULL,
  `short_name` varchar(50) NOT NULL,
  `registration_email` varchar(120) NOT NULL,
  `proof_document` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `approved_by_e_admin` tinyint(1) DEFAULT NULL,
  `approved_by_e_admin_time` datetime DEFAULT NULL,
  `approved_by_senior_e_admin` tinyint(1) DEFAULT NULL,
  `approved_by_senior_e_admin_time` datetime DEFAULT NULL,
  PRIMARY KEY (`organization_id`),
  UNIQUE KEY `registration_email` (`registration_email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organizations`
--

LOCK TABLES `organizations` WRITE;
/*!40000 ALTER TABLE `organizations` DISABLE KEYS */;
INSERT INTO `organizations` VALUES (1,'BEIJING NORMAL - HONG KONG BAPTIST UNIVERSITY ','UIC','123@uic.com','uploads/proof_documents\\p_srs_v4_b03.pdf','approved','2025-05-05 07:55:13',1,'2025-05-05 08:02:37',1,'2025-05-05 08:03:00'),(2,'HONG KONG UNIVERSITY','HKU','og2@hku.com','uploads/proof_documents\\Lab5Tasks.pdf','approved','2025-05-05 08:21:35',1,'2025-05-05 08:22:24',1,'2025-05-05 08:23:00'),(3,'System Organization','SYSTEM','system@edba.example.com',NULL,'approved','2025-05-17 10:39:23',1,NULL,1,NULL),(4,'Massachusetts Institute of Technology','MIT','mitconvener@mit.com','uploads/proof_documents\\9.pdf','approved','2025-05-18 16:30:24',1,'2025-05-18 16:32:17',1,'2025-05-18 16:32:40'),(5,'Imperial College London','IC','mike@ic.com','uploads/proof_documents\\2502268.pdf','rejected','2025-05-20 02:55:33',0,NULL,0,NULL),(6,'Imperial College London','IC','zoe@ic.com','uploads/proof_documents\\2502268.pdf','rejected','2025-05-20 03:02:22',0,NULL,0,NULL),(7,'Imperial College London','IC','lucy@ic.com','uploads/proof_documents\\2502268.pdf','approved','2025-05-20 03:05:28',1,'2025-05-20 03:05:55',1,'2025-05-20 03:06:36');
/*!40000 ALTER TABLE `organizations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `organization_id` int NOT NULL,
  `amount` float NOT NULL,
  `payment_type` varchar(50) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `service_id` int DEFAULT NULL,
  `receiver_organization_id` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`payment_id`),
  KEY `user_id` (`user_id`),
  KEY `organization_id` (`organization_id`),
  KEY `service_id` (`service_id`),
  KEY `receiver_organization_id` (`receiver_organization_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`),
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`),
  CONSTRAINT `payments_ibfk_4` FOREIGN KEY (`receiver_organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,5,2,100,'membership_fee','transfer',NULL,1,'2025-05-05 08:29:48',NULL,'pending'),(2,8,1,20,'thesis_download','quota',6,1,'2025-05-06 04:26:03','2025-05-06 04:26:03','pending'),(3,8,1,20,'thesis_download','transfer',6,1,'2025-05-06 04:52:36',NULL,'pending'),(4,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:03:56',NULL,'pending'),(5,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:05:26',NULL,'pending'),(6,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:08:29',NULL,'pending'),(7,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:16:14',NULL,'pending'),(8,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:17:10',NULL,'pending'),(9,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:17:53','2025-05-09 05:19:57','pending'),(10,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:25:50',NULL,'pending'),(11,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:27:43',NULL,'pending'),(12,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:45:14',NULL,'pending'),(13,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:46:20',NULL,'pending'),(14,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 05:48:12','2025-05-09 05:48:24','pending'),(15,7,2,20,'thesis_download','transfer',6,1,'2025-05-09 06:08:46','2025-05-09 06:08:52','pending'),(16,8,1,4,'student_identity','transfer',5,1,'2025-05-09 06:31:44',NULL,'pending'),(17,8,1,4,'student_identity','transfer',5,1,'2025-05-09 06:32:09','2025-05-09 06:32:33','pending'),(18,7,2,4,'student_identity','transfer',5,1,'2025-05-15 12:26:30',NULL,'pending'),(19,8,1,5,'student_record','transfer',8,1,'2025-05-15 12:59:16',NULL,'pending'),(20,8,1,5,'student_record','transfer',8,1,'2025-05-15 13:04:30',NULL,'pending'),(21,8,1,5,'student_record','transfer',8,1,'2025-05-15 13:24:28',NULL,'pending'),(22,8,1,5,'student_record','transfer',8,1,'2025-05-15 13:29:32',NULL,'pending'),(23,8,1,5,'student_record','transfer',8,1,'2025-05-15 13:42:34',NULL,'pending'),(24,8,1,5,'student_record','transfer',8,1,'2025-05-15 13:52:07',NULL,'pending'),(25,8,1,5,'student_record','transfer',8,1,'2025-05-15 14:09:24','2025-05-15 14:09:31','pending'),(26,7,2,5,'student_record','transfer',8,1,'2025-05-15 14:12:58','2025-05-15 14:13:30','pending'),(27,8,1,20,'thesis_download','transfer',6,1,'2025-05-15 14:21:57','2025-05-15 14:22:11','pending'),(28,7,2,20,'thesis_download','transfer',6,1,'2025-05-15 14:22:59','2025-05-15 14:23:09','pending'),(29,7,2,5,'student_record','transfer',8,1,'2025-05-16 07:02:27','2025-05-16 07:02:36','pending'),(30,7,2,5,'student_record','transfer',8,1,'2025-05-16 07:05:43',NULL,'pending'),(31,7,2,5,'student_record','transfer',8,1,'2025-05-16 07:08:04',NULL,'pending'),(32,7,2,5,'student_record','transfer',8,1,'2025-05-16 08:03:55','2025-05-16 08:15:25','pending'),(33,7,2,5,'student_record','transfer',8,1,'2025-05-16 08:22:23','2025-05-16 08:22:33','pending'),(34,7,2,5,'student_record','transfer',8,1,'2025-05-16 08:32:41','2025-05-16 08:32:53','pending'),(35,7,2,5,'student_record','transfer',8,1,'2025-05-16 08:36:43','2025-05-16 08:37:02','pending'),(36,7,2,5,'student_record','transfer',8,1,'2025-05-16 08:38:44','2025-05-16 08:38:54','pending'),(37,7,2,5,'student_record','transfer',8,1,'2025-05-16 08:41:11','2025-05-16 08:41:18','pending'),(38,7,2,4,'student_identity','transfer',5,1,'2025-05-16 08:42:20','2025-05-16 08:42:28','pending'),(39,7,2,5,'student_record','transfer',8,1,'2025-05-16 09:01:43','2025-05-16 09:01:52','pending'),(40,7,2,4,'student_identity','transfer',5,1,'2025-05-16 10:23:43','2025-05-16 10:23:56','pending'),(41,7,2,4,'student_identity','transfer',5,1,'2025-05-16 10:28:34','2025-05-16 10:28:42','pending'),(42,7,2,4,'student_identity','transfer',5,1,'2025-05-16 11:01:18','2025-05-16 11:01:42','pending'),(43,7,2,4,'student_identity','transfer',5,1,'2025-05-16 11:09:25','2025-05-16 11:09:32','pending'),(44,7,2,4,'student_identity','transfer',5,1,'2025-05-16 11:20:11','2025-05-16 11:20:19','pending'),(45,7,2,4,'student_identity','transfer',5,1,'2025-05-16 11:28:14','2025-05-16 11:28:20','pending'),(46,7,2,4,'student_identity','transfer',5,1,'2025-05-16 11:32:05','2025-05-16 11:32:15','pending'),(47,7,2,4,'student_identity','transfer',5,1,'2025-05-16 11:35:06','2025-05-16 11:35:14','pending'),(48,7,2,4,'student_identity','transfer',5,1,'2025-05-16 12:30:43','2025-05-16 12:30:50','pending'),(49,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 12:46:10','2025-05-16 12:46:18','pending'),(50,7,2,16,'student_identity_batch','transfer',5,1,'2025-05-16 12:58:24','2025-05-16 12:58:31','pending'),(51,7,2,16,'student_identity_batch','transfer',5,1,'2025-05-16 13:02:59','2025-05-16 13:03:08','pending'),(52,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 13:12:26','2025-05-16 13:12:33','pending'),(53,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 13:21:15','2025-05-16 13:21:25','pending'),(54,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 13:23:40','2025-05-16 13:23:53','pending'),(55,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 13:37:03','2025-05-16 13:37:12','pending'),(56,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 13:44:33','2025-05-16 13:44:40','pending'),(57,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 13:45:20','2025-05-16 13:45:27','pending'),(58,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 13:47:43','2025-05-16 13:47:49','pending'),(59,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 13:48:30','2025-05-16 13:51:01','pending'),(60,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 13:51:41','2025-05-16 13:53:23','pending'),(61,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 14:07:58','2025-05-16 14:08:04','pending'),(62,7,2,8,'student_identity_batch','transfer',5,1,'2025-05-16 14:12:19','2025-05-16 14:12:25','used'),(63,7,2,4,'student_identity','transfer',5,1,'2025-05-16 14:12:50','2025-05-16 14:12:57','used'),(64,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 14:17:45','2025-05-16 14:17:55','used'),(65,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 14:35:17','2025-05-16 14:35:28','used'),(66,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 14:35:40','2025-05-16 14:35:47','used'),(67,7,2,4,'student_identity','transfer',5,1,'2025-05-16 14:35:57','2025-05-16 14:36:05','used'),(68,7,2,4,'student_identity','transfer',5,1,'2025-05-16 14:36:28','2025-05-16 14:36:36','used'),(69,7,2,4,'student_identity','transfer',5,1,'2025-05-16 14:37:57','2025-05-16 14:38:04','used'),(70,7,2,4,'student_identity','transfer',5,1,'2025-05-16 14:50:07','2025-05-16 14:50:14','used'),(71,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-16 14:51:14','2025-05-16 14:51:21','used'),(72,7,2,4,'student_identity','transfer',5,1,'2025-05-16 14:51:36','2025-05-16 14:51:43','used'),(73,8,1,4,'student_identity','transfer',5,1,'2025-05-17 09:05:46',NULL,'pending'),(74,7,2,4,'student_identity','transfer',5,1,'2025-05-17 09:06:42','2025-05-17 09:06:49','used'),(75,7,2,4,'student_identity','transfer',5,1,'2025-05-17 09:07:04','2025-05-17 09:07:11','used'),(76,7,2,12,'student_identity_batch','transfer',5,1,'2025-05-17 09:07:21','2025-05-17 09:07:28','used'),(77,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:07:44','2025-05-17 09:08:07','failed'),(78,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:11:22','2025-05-17 09:11:33','used'),(79,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:17:30','2025-05-17 09:17:36','used'),(80,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:18:03','2025-05-17 09:18:09','used'),(81,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:18:19','2025-05-17 09:18:25','used'),(82,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 09:19:06','2025-05-17 09:19:12','completed'),(83,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 09:43:28','2025-05-17 09:43:35','used'),(84,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:44:55','2025-05-17 09:45:01','used'),(85,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:45:16','2025-05-17 09:45:23','used'),(86,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 09:47:33','2025-05-17 09:47:40','used'),(87,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:47:49','2025-05-17 09:47:55','used'),(88,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 09:48:04','2025-05-17 09:48:12','used'),(89,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:53:39','2025-05-17 09:53:46','used'),(90,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:53:57','2025-05-17 09:54:03','used'),(91,7,2,5,'student_record','transfer',8,1,'2025-05-17 09:58:44','2025-05-17 09:58:52','used'),(92,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 09:59:42','2025-05-17 09:59:49','used'),(93,7,2,5,'student_record','transfer',8,1,'2025-05-17 10:01:11','2025-05-17 10:01:18','used'),(94,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 10:03:44','2025-05-17 10:03:52','used'),(95,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 10:04:02','2025-05-17 10:04:09','used'),(96,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 10:04:21','2025-05-17 10:04:28','used'),(97,7,2,15,'student_record_batch','transfer',8,1,'2025-05-17 10:05:12','2025-05-17 10:05:19','used'),(98,7,2,5,'student_record','transfer',8,1,'2025-05-17 10:05:26','2025-05-17 10:05:32','used'),(99,4,1,100,'membership_fee','transfer',NULL,1,'2025-05-17 10:41:25','2025-05-17 10:41:38','completed'),(100,4,1,100,'membership_fee','transfer',NULL,1,'2025-05-17 10:44:13',NULL,'pending'),(101,4,1,100,'membership_fee','transfer',NULL,1,'2025-05-17 10:48:43',NULL,'pending'),(102,4,1,1000,'membership_upgrade','transfer',NULL,3,'2025-05-17 11:09:02','2025-05-17 11:09:38','completed'),(103,4,1,1000,'membership_upgrade','transfer',NULL,3,'2025-05-17 11:09:57',NULL,'pending'),(104,5,2,25,'membership_fee','transfer',NULL,3,'2025-05-17 11:44:13','2025-05-17 11:44:36','completed'),(105,5,2,30,'membership_upgrade','transfer',NULL,3,'2025-05-17 11:45:11',NULL,'pending'),(106,5,2,40,'membership_upgrade','transfer',NULL,3,'2025-05-17 12:12:36','2025-05-17 12:12:47','completed'),(107,5,2,20,'membership_upgrade','transfer',NULL,3,'2025-05-17 12:13:55',NULL,'pending'),(108,5,2,40,'membership_upgrade','transfer',NULL,3,'2025-05-17 12:16:22','2025-05-17 12:16:31','completed'),(109,5,2,30,'membership_upgrade','transfer',NULL,3,'2025-05-17 12:16:57','2025-05-17 12:17:08','completed'),(110,5,2,30,'membership_upgrade','transfer',NULL,3,'2025-05-17 12:17:20','2025-05-17 12:17:26','completed'),(111,5,2,90,'membership_fee_batch','transfer',NULL,3,'2025-05-17 12:17:35','2025-05-17 12:18:05','completed'),(112,4,1,90,'membership_fee_batch','transfer',NULL,3,'2025-05-17 14:13:46',NULL,'pending'),(113,4,1,90,'membership_fee_batch','transfer',NULL,3,'2025-05-17 14:14:36','2025-05-17 15:00:08','completed'),(114,4,1,90,'membership_fee_batch','transfer',NULL,3,'2025-05-17 15:01:55','2025-05-17 15:02:14','completed'),(115,5,2,90,'membership_fee_batch','transfer',NULL,3,'2025-05-17 16:34:57','2025-05-17 16:35:07','completed'),(116,4,1,20,'membership_fee','transfer',NULL,3,'2025-05-17 17:22:21',NULL,'pending'),(117,4,1,20,'membership_fee','transfer',NULL,3,'2025-05-17 17:23:42',NULL,'pending'),(118,4,1,40,'membership_fee','transfer',NULL,3,'2025-05-17 17:37:33',NULL,'pending'),(119,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 17:48:02','2025-05-17 17:58:43','failed'),(120,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 18:00:36','2025-05-17 18:00:44','failed'),(121,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 18:05:41','2025-05-17 18:13:30','used'),(122,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 18:14:57','2025-05-17 18:15:03','used'),(123,4,1,90,'membership_fee_batch','transfer',NULL,3,'2025-05-17 18:24:27',NULL,'pending'),(124,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 18:28:30','2025-05-17 18:28:37','used'),(125,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 18:29:44',NULL,'pending'),(126,7,2,20,'thesis_download','transfer',6,1,'2025-05-17 18:35:17','2025-05-17 18:35:28','used'),(127,29,4,30,'membership_fee','transfer',NULL,3,'2025-05-18 16:34:19','2025-05-18 16:34:27','completed'),(128,9,1,10,'student_identity_batch','transfer',11,4,'2025-05-18 16:46:26','2025-05-18 16:46:33','used'),(129,9,1,30,'student_identity_batch','transfer',11,4,'2025-05-18 16:52:45','2025-05-18 16:52:54','used'),(130,9,1,30,'student_record_batch','transfer',13,4,'2025-05-19 01:19:30','2025-05-19 01:19:39','used'),(131,9,1,5,'student_record','transfer',13,4,'2025-05-19 09:01:42',NULL,'pending'),(132,9,1,5,'student_record','transfer',8,1,'2025-05-19 09:59:09',NULL,'pending'),(133,9,1,5,'student_record','transfer',8,1,'2025-05-19 10:33:34','2025-05-19 10:38:31','used'),(134,9,1,5,'student_record','transfer',13,4,'2025-05-19 10:52:12',NULL,'pending'),(135,9,1,5,'student_record','transfer',13,4,'2025-05-19 10:52:24','2025-05-19 10:52:28','used'),(136,34,7,30,'membership_fee','transfer',NULL,3,'2025-05-20 03:34:52','2025-05-20 03:35:00','completed'),(137,34,7,1130,'membership_fee_batch','transfer',NULL,3,'2025-05-20 03:35:40','2025-05-20 03:35:48','completed'),(138,34,7,20,'membership_fee','transfer',NULL,3,'2025-05-20 03:39:05',NULL,'pending'),(139,34,7,100000000000000,'membership_fee','transfer',NULL,3,'2025-05-20 03:42:41',NULL,'failed'),(140,46,7,10,'thesis_download','transfer',15,7,'2025-05-20 07:17:17',NULL,'pending'),(141,46,7,10,'thesis_download','transfer',15,7,'2025-05-20 07:19:23','2025-05-20 07:19:34','used'),(142,46,7,10,'thesis_download','transfer',15,7,'2025-05-20 07:20:12','2025-05-20 07:20:16','used'),(143,46,7,10,'thesis_download','transfer',15,7,'2025-05-20 07:21:04','2025-05-20 07:21:07','used'),(144,46,7,10,'thesis_download','transfer',15,7,'2025-05-20 07:27:42','2025-05-20 07:27:45','used'),(145,46,7,10,'thesis_download','transfer',15,7,'2025-05-20 07:27:56','2025-05-20 07:27:59','used'),(146,16,2,20,'thesis_download','transfer',6,1,'2025-05-20 07:32:15','2025-05-20 07:32:19','used'),(147,34,7,1000,'membership_fee','transfer',NULL,3,'2025-05-20 07:33:36',NULL,'pending'),(148,34,7,1000,'membership_fee','transfer',NULL,3,'2025-05-20 07:34:22','2025-05-20 07:34:26','completed'),(149,9,1,10,'thesis_download','transfer',15,7,'2025-05-20 07:39:48','2025-05-20 07:39:52','used'),(150,9,1,10,'thesis_download','transfer',15,7,'2025-05-20 07:43:10','2025-05-20 07:43:18','used'),(151,9,1,3,'student_identity','transfer',16,7,'2025-05-20 07:55:46',NULL,'pending'),(152,4,1,20,'membership_upgrade','transfer',NULL,3,'2025-05-20 07:56:21','2025-05-20 07:56:28','completed'),(153,9,1,3,'student_identity','transfer',16,7,'2025-05-20 07:56:44',NULL,'pending'),(154,9,1,3,'student_identity','transfer',16,7,'2025-05-20 07:57:35','2025-05-20 07:57:39','used'),(155,9,1,18,'student_identity_batch','transfer',16,7,'2025-05-20 07:58:09',NULL,'pending'),(156,9,1,18,'student_identity_batch','transfer',16,7,'2025-05-20 07:58:21','2025-05-20 07:58:24','used'),(157,9,1,18,'student_identity_batch','transfer',16,7,'2025-05-20 07:59:21','2025-05-20 07:59:24','used'),(158,9,1,18,'student_identity_batch','transfer',16,7,'2025-05-20 08:00:18','2025-05-20 08:00:23','used'),(159,9,1,5,'student_record','transfer',17,7,'2025-05-20 08:03:15','2025-05-20 08:03:22','used'),(160,9,1,30,'student_record_batch','transfer',17,7,'2025-05-20 08:03:40','2025-05-20 08:03:45','used');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `policies`
--

DROP TABLE IF EXISTS `policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policies` (
  `policy_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`policy_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `policies`
--

LOCK TABLES `policies` WRITE;
/*!40000 ALTER TABLE `policies` DISABLE KEYS */;
INSERT INTO `policies` VALUES (2,'policy test','uploads/policies/A1_s230016081.pdf','2025-05-20 03:28:13','2025-05-20 03:28:55','this is a try');
/*!40000 ALTER TABLE `policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_access`
--

DROP TABLE IF EXISTS `service_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service_access` (
  `service_id` int NOT NULL,
  `organization_id` int NOT NULL,
  PRIMARY KEY (`service_id`,`organization_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `service_access_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`),
  CONSTRAINT `service_access_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_access`
--

LOCK TABLES `service_access` WRITE;
/*!40000 ALTER TABLE `service_access` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_download_access`
--

DROP TABLE IF EXISTS `service_download_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service_download_access` (
  `service_id` int NOT NULL,
  `organization_id` int NOT NULL,
  PRIMARY KEY (`service_id`,`organization_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `service_download_access_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`),
  CONSTRAINT `service_download_access_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_download_access`
--

LOCK TABLES `service_download_access` WRITE;
/*!40000 ALTER TABLE `service_download_access` DISABLE KEYS */;
INSERT INTO `service_download_access` VALUES (3,1),(12,1),(15,1),(5,2),(6,2),(15,4),(15,5);
/*!40000 ALTER TABLE `service_download_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_view_access`
--

DROP TABLE IF EXISTS `service_view_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service_view_access` (
  `service_id` int NOT NULL,
  `organization_id` int NOT NULL,
  PRIMARY KEY (`service_id`,`organization_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `service_view_access_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`),
  CONSTRAINT `service_view_access_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_view_access`
--

LOCK TABLES `service_view_access` WRITE;
/*!40000 ALTER TABLE `service_view_access` DISABLE KEYS */;
INSERT INTO `service_view_access` VALUES (3,1),(12,1),(15,1),(5,2),(6,2),(12,2),(15,2),(12,3),(15,3),(15,4),(15,5),(15,6);
/*!40000 ALTER TABLE `service_view_access` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services` (
  `service_id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `description` text,
  `price` float DEFAULT NULL,
  `is_configured` tinyint(1) DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`service_id`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `services_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services`
--

LOCK TABLES `services` WRITE;
/*!40000 ALTER TABLE `services` DISABLE KEYS */;
INSERT INTO `services` VALUES (1,1,'UIC course','course_info','',0,1,1,'2025-05-05 08:03:35'),(3,2,'HKU thesis','thesis_sharing','yy',10,0,1,'2025-05-05 08:23:56'),(5,1,'UIC student authenciation','student_identity','',4,1,1,'2025-05-05 17:02:04'),(6,1,'UIC thesis','thesis_sharing','',20,1,1,'2025-05-05 17:02:21'),(7,2,'HKU course','course_info','',0,1,1,'2025-05-05 17:42:28'),(8,1,'UIC student GPA Record','student_record','',5,1,1,'2025-05-09 04:56:47'),(10,4,'MIT Course','course_info','here is some public course information from MIT',0,1,1,'2025-05-18 16:35:29'),(11,4,'MIT student identity','student_identity','check if the student is from MIT or not',5,1,1,'2025-05-18 16:35:49'),(12,4,'MIT thesis','thesis_sharing','here is some thesis from MIT',20,1,1,'2025-05-18 16:36:04'),(13,4,'MIT student GPA Record','student_record','here you can check the student gpa record from MIT',5,1,1,'2025-05-19 01:17:38'),(15,7,'IC thesis','thesis_sharing','thesis info',10,1,1,'2025-05-20 03:50:06'),(16,7,'IC student idenity','student_identity','ifo',3,1,1,'2025-05-20 03:57:03'),(17,7,'ic student GPA record','student_record','',5,1,1,'2025-05-20 04:24:32'),(18,7,'IC course','course_info','course info',0,1,1,'2025-05-20 08:08:00');
/*!40000 ALTER TABLE `services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(255) DEFAULT NULL,
  `data` blob,
  `expiry` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_id` (`session_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
INSERT INTO `sessions` VALUES (1,'session:SPAUA99CJilnl1lazoAnjcLMLd-d-zCo-fs3ZBSfO8U',_binary '��_permanentñverification_code�277361�verification_email�cyj@uic.com�session_id\�$1f41ba3c-b9a7-4ee8-ad8a-97cab7146007�user_id�user_email�cyj@uic.com�user_role�user�user_access_level�organization_id','2025-05-06 17:52:22');
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `payment_id` int DEFAULT NULL,
  `from_organization_id` int NOT NULL,
  `to_organization_id` int NOT NULL,
  `amount` float NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `reason` text,
  `transaction_time` datetime DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `payment_id` (`payment_id`),
  KEY `from_organization_id` (`from_organization_id`),
  KEY `to_organization_id` (`to_organization_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`payment_id`),
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`from_organization_id`) REFERENCES `organizations` (`organization_id`),
  CONSTRAINT `transactions_ibfk_3` FOREIGN KEY (`to_organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=142 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (1,7,2,1,20,'failed','未知原因','2025-05-09 05:16:23'),(2,8,2,1,20,'failed','authentication failed','2025-05-09 05:17:24'),(3,9,2,1,20,'success',NULL,'2025-05-09 05:19:57'),(4,10,2,1,20,'failed','未知原因','2025-05-09 05:25:54'),(5,11,2,1,20,'failed','未知原因','2025-05-09 05:37:50'),(6,14,2,1,20,'success',NULL,'2025-05-09 05:48:24'),(7,15,2,1,20,'success',NULL,'2025-05-09 06:08:52'),(8,16,1,1,4,'failed','authentication failed','2025-05-09 06:31:50'),(9,17,1,1,4,'success',NULL,'2025-05-09 06:32:33'),(10,18,2,1,4,'failed','Expecting value: line 1 column 1 (char 0)','2025-05-15 12:27:16'),(11,19,1,1,5,'failed','Expecting value: line 1 column 1 (char 0)','2025-05-15 13:01:27'),(12,20,1,1,5,'failed','Expecting value: line 1 column 1 (char 0)','2025-05-15 13:04:36'),(13,21,1,1,5,'failed','Expecting value: line 1 column 1 (char 0)','2025-05-15 13:24:58'),(14,23,1,1,5,'failed','Expecting value: line 1 column 1 (char 0)','2025-05-15 13:51:33'),(15,24,1,1,5,'failed','Expecting value: line 1 column 1 (char 0)','2025-05-15 13:53:34'),(16,25,1,1,5,'success',NULL,'2025-05-15 14:09:31'),(17,26,2,1,5,'success',NULL,'2025-05-15 14:13:30'),(18,27,1,1,20,'success',NULL,'2025-05-15 14:22:11'),(19,28,2,1,20,'success',NULL,'2025-05-15 14:23:09'),(20,29,2,1,5,'success',NULL,'2025-05-16 07:02:36'),(21,32,2,1,5,'success',NULL,'2025-05-16 08:15:25'),(22,33,2,1,5,'success',NULL,'2025-05-16 08:22:33'),(23,34,2,1,5,'success',NULL,'2025-05-16 08:32:53'),(24,35,2,1,5,'success',NULL,'2025-05-16 08:37:02'),(25,36,2,1,5,'success',NULL,'2025-05-16 08:38:54'),(26,37,2,1,5,'success',NULL,'2025-05-16 08:41:18'),(27,38,2,1,4,'success',NULL,'2025-05-16 08:42:28'),(28,39,2,1,5,'success',NULL,'2025-05-16 09:01:52'),(29,40,2,1,4,'success',NULL,'2025-05-16 10:23:56'),(30,41,2,1,4,'success',NULL,'2025-05-16 10:28:42'),(31,42,2,1,4,'success',NULL,'2025-05-16 11:01:42'),(32,43,2,1,4,'success',NULL,'2025-05-16 11:09:32'),(33,44,2,1,4,'success',NULL,'2025-05-16 11:20:19'),(34,45,2,1,4,'success',NULL,'2025-05-16 11:28:20'),(35,46,2,1,4,'success',NULL,'2025-05-16 11:32:15'),(36,47,2,1,4,'success',NULL,'2025-05-16 11:35:14'),(37,48,2,1,4,'success',NULL,'2025-05-16 12:30:50'),(38,49,2,1,12,'success',NULL,'2025-05-16 12:46:18'),(39,50,2,1,16,'success',NULL,'2025-05-16 12:58:31'),(40,51,2,1,16,'success',NULL,'2025-05-16 13:03:08'),(41,52,2,1,12,'success',NULL,'2025-05-16 13:12:33'),(42,53,2,1,12,'success',NULL,'2025-05-16 13:21:25'),(43,54,2,1,12,'success',NULL,'2025-05-16 13:23:53'),(44,55,2,1,8,'success',NULL,'2025-05-16 13:37:12'),(45,56,2,1,8,'failed','Could not build url for endpoint \'consumer.student_auth_batch_result\' with values [\'batch_size\', \'service_id\', \'temp_file\']. Did you mean \'consumer.student_auth_result\' instead?','2025-05-16 13:44:40'),(46,57,2,1,8,'failed','Could not build url for endpoint \'consumer.student_auth_batch_result\' with values [\'batch_size\', \'service_id\', \'temp_file\']. Did you mean \'consumer.student_auth_result\' instead?','2025-05-16 13:45:27'),(47,58,2,1,12,'failed','Could not build url for endpoint \'consumer.student_auth_batch_result\' with values [\'batch_size\', \'service_id\', \'temp_file\']. Did you mean \'consumer.student_auth_result\' instead?','2025-05-16 13:47:49'),(48,59,2,1,8,'success',NULL,'2025-05-16 13:48:37'),(49,59,2,1,8,'failed','Could not build url for endpoint \'consumer.student_auth_batch_result\' with values [\'service_id\']. Did you mean \'consumer.student_auth_result\' instead?','2025-05-16 13:51:01'),(50,60,2,1,8,'success',NULL,'2025-05-16 13:51:47'),(51,60,2,1,8,'success',NULL,'2025-05-16 13:53:23'),(52,61,2,1,8,'success',NULL,'2025-05-16 14:08:04'),(53,62,2,1,8,'success',NULL,'2025-05-16 14:12:25'),(54,63,2,1,4,'success',NULL,'2025-05-16 14:12:57'),(55,64,2,1,12,'success',NULL,'2025-05-16 14:17:55'),(56,65,2,1,12,'success',NULL,'2025-05-16 14:35:28'),(57,66,2,1,12,'success',NULL,'2025-05-16 14:35:47'),(58,67,2,1,4,'success',NULL,'2025-05-16 14:36:05'),(59,68,2,1,4,'success',NULL,'2025-05-16 14:36:36'),(60,69,2,1,4,'success',NULL,'2025-05-16 14:38:04'),(61,70,2,1,4,'success',NULL,'2025-05-16 14:50:14'),(62,71,2,1,12,'success',NULL,'2025-05-16 14:51:21'),(63,72,2,1,4,'success',NULL,'2025-05-16 14:51:43'),(64,74,2,1,4,'success',NULL,'2025-05-17 09:06:49'),(65,75,2,1,4,'success',NULL,'2025-05-17 09:07:11'),(66,76,2,1,12,'success',NULL,'2025-05-17 09:07:28'),(67,77,2,1,5,'failed','Could not build url for endpoint \'consumer.student_record_result\' with values [\'id\', \'name\', \'query_type\', \'service_id\']. Did you mean \'consumer.student_record\' instead?','2025-05-17 09:08:07'),(68,78,2,1,5,'success',NULL,'2025-05-17 09:11:33'),(69,79,2,1,5,'success',NULL,'2025-05-17 09:17:36'),(70,80,2,1,5,'success',NULL,'2025-05-17 09:18:09'),(71,81,2,1,5,'success',NULL,'2025-05-17 09:18:25'),(72,82,2,1,15,'success',NULL,'2025-05-17 09:19:12'),(73,83,2,1,15,'success',NULL,'2025-05-17 09:43:35'),(74,84,2,1,5,'success',NULL,'2025-05-17 09:45:01'),(75,85,2,1,5,'success',NULL,'2025-05-17 09:45:23'),(76,86,2,1,15,'success',NULL,'2025-05-17 09:47:40'),(77,87,2,1,5,'success',NULL,'2025-05-17 09:47:55'),(78,88,2,1,15,'success',NULL,'2025-05-17 09:48:12'),(79,89,2,1,5,'success',NULL,'2025-05-17 09:53:46'),(80,90,2,1,5,'success',NULL,'2025-05-17 09:54:03'),(81,91,2,1,5,'success',NULL,'2025-05-17 09:58:52'),(82,92,2,1,15,'success',NULL,'2025-05-17 09:59:49'),(83,93,2,1,5,'success',NULL,'2025-05-17 10:01:18'),(84,94,2,1,15,'success',NULL,'2025-05-17 10:03:51'),(85,94,2,1,15,'success',NULL,'2025-05-17 10:03:52'),(86,95,2,1,15,'success',NULL,'2025-05-17 10:04:09'),(87,96,2,1,15,'success',NULL,'2025-05-17 10:04:28'),(88,97,2,1,15,'success',NULL,'2025-05-17 10:05:19'),(89,98,2,1,5,'success',NULL,'2025-05-17 10:05:32'),(90,99,1,1,100,'success',NULL,'2025-05-17 10:41:38'),(91,102,1,3,1000,'success',NULL,'2025-05-17 11:09:38'),(92,104,2,3,25,'success',NULL,'2025-05-17 11:44:36'),(93,106,2,3,40,'success',NULL,'2025-05-17 12:12:47'),(94,108,2,3,40,'success',NULL,'2025-05-17 12:16:31'),(95,109,2,3,30,'success',NULL,'2025-05-17 12:17:08'),(96,110,2,3,30,'success',NULL,'2025-05-17 12:17:26'),(97,111,2,3,90,'success',NULL,'2025-05-17 12:18:05'),(98,113,1,3,90,'success',NULL,'2025-05-17 14:24:08'),(99,113,1,3,90,'success',NULL,'2025-05-17 14:39:35'),(100,113,1,3,90,'success',NULL,'2025-05-17 14:40:36'),(101,113,1,3,90,'success',NULL,'2025-05-17 14:44:25'),(102,113,1,3,90,'success',NULL,'2025-05-17 14:50:47'),(103,113,1,3,90,'success',NULL,'2025-05-17 15:00:08'),(104,114,1,3,90,'success',NULL,'2025-05-17 15:02:14'),(105,115,2,3,90,'success',NULL,'2025-05-17 16:35:07'),(106,119,2,1,20,'success',NULL,'2025-05-17 17:48:15'),(107,119,2,1,20,'success',NULL,'2025-05-17 17:48:19'),(108,119,2,1,20,'success',NULL,'2025-05-17 17:53:38'),(109,119,2,1,20,'failed','Could not build url for endpoint \'consumer.thesis_download\'. Did you forget to specify values [\'service_id\']?','2025-05-17 17:58:43'),(110,120,2,1,20,'failed','Could not build url for endpoint \'consumer.thesis_download_after_payment\'. Did you forget to specify values [\'service_id\']?','2025-05-17 18:00:44'),(111,121,2,1,20,'success',NULL,'2025-05-17 18:05:50'),(112,121,2,1,20,'success',NULL,'2025-05-17 18:13:16'),(113,121,2,1,20,'success',NULL,'2025-05-17 18:13:30'),(114,122,2,1,20,'success',NULL,'2025-05-17 18:15:03'),(115,124,2,1,20,'success',NULL,'2025-05-17 18:28:37'),(116,126,2,1,20,'success',NULL,'2025-05-17 18:35:28'),(117,127,4,3,30,'success',NULL,'2025-05-18 16:34:27'),(118,128,1,4,10,'success',NULL,'2025-05-18 16:46:33'),(119,129,1,4,30,'success',NULL,'2025-05-18 16:52:54'),(120,130,1,4,30,'success',NULL,'2025-05-19 01:19:39'),(121,133,1,1,5,'success',NULL,'2025-05-19 10:38:31'),(122,135,1,4,5,'success',NULL,'2025-05-19 10:52:28'),(123,136,7,3,30,'success',NULL,'2025-05-20 03:35:00'),(124,137,7,3,1130,'success',NULL,'2025-05-20 03:35:48'),(125,139,7,3,100000000000000,'failed','insufficient funds','2025-05-20 03:42:49'),(126,141,7,7,10,'success',NULL,'2025-05-20 07:19:34'),(127,142,7,7,10,'success',NULL,'2025-05-20 07:20:16'),(128,143,7,7,10,'success',NULL,'2025-05-20 07:21:07'),(129,144,7,7,10,'success',NULL,'2025-05-20 07:27:45'),(130,145,7,7,10,'success',NULL,'2025-05-20 07:27:59'),(131,146,2,1,20,'success',NULL,'2025-05-20 07:32:19'),(132,148,7,3,1000,'success',NULL,'2025-05-20 07:34:26'),(133,149,1,7,10,'success',NULL,'2025-05-20 07:39:52'),(134,150,1,7,10,'success',NULL,'2025-05-20 07:43:18'),(135,152,1,3,20,'success',NULL,'2025-05-20 07:56:28'),(136,154,1,7,3,'success',NULL,'2025-05-20 07:57:39'),(137,156,1,7,18,'success',NULL,'2025-05-20 07:58:24'),(138,157,1,7,18,'success',NULL,'2025-05-20 07:59:24'),(139,158,1,7,18,'success',NULL,'2025-05-20 08:00:23'),(140,159,1,7,5,'success',NULL,'2025-05-20 08:03:22'),(141,160,1,7,30,'success',NULL,'2025-05-20 08:03:45');
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `organization_id` int DEFAULT NULL,
  `access_level` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `last_login` datetime DEFAULT NULL,
  `is_wildcard_user` tinyint(1) NOT NULL DEFAULT '0',
  `wildcard_source` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`organization_id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'tadmin@edba.example.com','scrypt:32768:8:1$RkUKKoVyDRSLquLx$4ec5f5ef0368263533b5909e35a2ecee2d41fc13b829980c8487cdf886cc5176cead4519489368a90e079c1794e44ac0c7d786041f0d83d473499a0b13f7ff01',NULL,1,'2025-05-05 07:52:47','T-Admin',1,'2025-05-20 07:10:38',0,NULL),(2,'admin@edba.com','scrypt:32768:8:1$nw1l0OHffdbCwx8Q$a95797e7c186241ee15afd5e818ccbb6dd8fb03bf78d48c3ac257778c9d9bfe3d43d56db1c61ac25609343ea556750de714440374c3b550afe7e5ff3a475fb41',NULL,1,'2025-05-05 07:53:30','E-Admin',1,'2025-05-20 04:02:21',0,NULL),(3,'sadmin@edba.com','scrypt:32768:8:1$MrBi9sQqsqXcxi6I$176478aac4af36ecf4e4c2c170d6904284f0e6091bcb608030306d7b295bb9e32f1fb66036715ed5ef745583151ce477d1e7a49fb6f8e5f2c98d50aefb11c3c8',NULL,1,'2025-05-05 07:53:36','Senior-E-Admin',1,'2025-05-20 03:06:20',0,NULL),(4,'123@uic.com',NULL,1,3,'2025-05-05 08:03:00','O-Convener',1,'2025-05-20 08:09:00',0,NULL),(5,'og2@gmail.com',NULL,2,3,'2025-05-05 08:23:00','O-Convener',1,'2025-05-17 16:32:42',0,NULL),(7,'cyj@gmail.com',NULL,2,3,'2025-05-05 08:29:48','user',1,'2025-05-17 18:28:20',0,NULL),(8,'cyj@uic.com',NULL,NULL,3,'2025-05-05 16:12:58','user',1,'2025-05-20 07:47:28',0,NULL),(9,'zl@uic.com',NULL,1,2,'2025-05-17 10:10:29','user',1,'2025-05-20 07:55:24',0,NULL),(10,'tyy@uic.com',NULL,1,3,'2025-05-17 10:10:43','user',1,NULL,0,NULL),(12,'lele@hku.com',NULL,1,3,'2025-05-17 10:47:44','user',1,NULL,0,NULL),(14,'lelezhou@uic.com',NULL,1,1,'2025-05-17 10:48:43','user',1,NULL,0,NULL),(15,'aaa@uic.com',NULL,1,1,'2025-05-17 11:05:08','user',1,'2025-05-20 08:06:55',0,NULL),(16,'aaa@gmail.com',NULL,2,3,'2025-05-17 11:44:13','user',1,'2025-05-20 07:32:02',0,NULL),(19,'123@example.com',NULL,2,3,'2025-05-17 12:18:37','user',1,NULL,0,NULL),(21,'haha@example.com',NULL,1,3,'2025-05-17 15:05:22','user',1,'2025-05-17 15:06:17',1,'*@example.com'),(22,'zhangsan@gmail.com',NULL,2,2,'2025-05-17 16:35:07','user',1,'2025-05-17 16:38:53',0,NULL),(23,'lisi@gmail.com',NULL,2,3,'2025-05-17 16:35:07','user',1,NULL,0,NULL),(24,'new@public.hku.com',NULL,2,1,'2025-05-17 16:36:49','user',1,'2025-05-17 16:54:05',1,'*@public.hku.com'),(25,'new2@public.hku.com',NULL,2,1,'2025-05-17 16:37:49','user',1,'2025-05-17 16:37:49',1,'*@public.hku.com'),(29,'mitconvener@mit.com',NULL,4,3,'2025-05-18 16:32:40','O-Convener',1,'2025-05-19 01:00:45',0,NULL),(30,'mitprovider@mit.com',NULL,4,3,'2025-05-18 16:34:27','user',1,'2025-05-19 01:18:05',0,NULL),(31,'eadmin2@edba.com',NULL,NULL,1,'2025-05-19 11:08:51','E-Admin',1,NULL,0,NULL),(32,'eadmin3@edba.com',NULL,NULL,1,'2025-05-19 11:10:42','E-Admin',1,NULL,0,NULL),(33,'seadmin3@edba.com',NULL,NULL,1,'2025-05-19 11:10:49','Senior-E-Admin',1,NULL,0,NULL),(34,'lucy@ic.com',NULL,7,3,'2025-05-20 03:06:36','O-Convener',1,'2025-05-20 08:07:46',0,NULL),(35,'chen@ic.com',NULL,7,3,'2025-05-20 03:35:00','user',1,NULL,0,NULL),(36,'joyce@ic.com',NULL,7,3,'2025-05-20 03:35:48','user',1,'2025-05-20 08:02:08',0,NULL),(38,'zeo@ic.com',NULL,7,2,'2025-05-20 03:35:48','user',1,'2025-05-20 03:48:08',0,NULL),(39,'lily@ic.com',NULL,7,3,'2025-05-20 03:35:48','user',1,NULL,0,NULL),(40,'lele@ic.com',NULL,7,2,'2025-05-20 03:35:48','user',1,'2025-05-20 07:44:57',0,NULL),(41,'eadmin4@edba.com',NULL,NULL,1,'2025-05-20 04:03:55','E-Admin',1,'2025-05-20 04:04:19',0,NULL),(42,'sadmin4@edba.com',NULL,NULL,1,'2025-05-20 04:05:06','Senior-E-Admin',1,'2025-05-20 04:05:26',0,NULL),(43,'new@public.ic.com',NULL,7,1,'2025-05-20 07:03:54','user',1,'2025-05-20 07:04:28',1,'*@public.ic.com'),(44,'new1@public.ic.com',NULL,7,1,'2025-05-20 07:05:56','user',1,'2025-05-20 07:05:56',1,'*@public.ic.com'),(45,'newuser@public.ic.com',NULL,7,1,'2025-05-20 07:07:10','user',1,'2025-05-20 07:07:10',1,'*@public.ic.com'),(46,'chenchen@public.ic.com',NULL,7,1,'2025-05-20 07:08:24','user',1,'2025-05-20 07:08:24',1,'*@public.ic.com'),(47,'neo@ic.com',NULL,7,1,'2025-05-20 07:34:26','user',1,'2025-05-20 07:34:48',0,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-20 17:09:54
