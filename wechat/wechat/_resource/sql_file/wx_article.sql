/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50718
 Source Host           : localhost
 Source Database       : stcms

 Target Server Type    : MySQL
 Target Server Version : 50718
 File Encoding         : utf-8

 Date: 07/23/2017 22:51:58 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `wx_article`
-- ----------------------------
DROP TABLE IF EXISTS `wx_article`;
CREATE TABLE `wx_article` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `md5id` varchar(255) DEFAULT NULL COMMENT '文章 md5 标识',
  `title` varchar(200) DEFAULT NULL COMMENT '标题',
  `author` varchar(50) DEFAULT NULL COMMENT '作者',
  `thumb` varchar(255) DEFAULT NULL COMMENT '封面',
  `digest` text COMMENT '摘要',
  `idx` varchar(100) DEFAULT NULL,
  `copyright_stat` int(10) DEFAULT NULL COMMENT '版权信息',
  `biz` varchar(255) DEFAULT NULL COMMENT '公号 唯一标识',
  `datetime` int(10) DEFAULT NULL COMMENT '文章发布日期',
  `status` tinyint(1) DEFAULT '0' COMMENT '状态',
  `created_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '采集时间',
  PRIMARY KEY (`id`),
  KEY `author` (`author`) USING BTREE,
  KEY `title` (`title`) USING BTREE,
  KEY `biz` (`biz`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
