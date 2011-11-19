-- MySQL dump 8.23
--
-- Host: localhost    Database: traffic
---------------------------------------------------------
-- Server version	3.23.58

--
-- Table structure for table `iptables`
--

CREATE TABLE iptables (
  comp varchar(16) default NULL,
  state varchar(255) default NULL,
  bytes int(11) default NULL
) TYPE=MyISAM;

--
-- Table structure for table `sessions`
--

CREATE TABLE sessions (
  begin timestamp(14) NOT NULL,
  end timestamp(14) NOT NULL,
  admin varchar(255) NOT NULL default '',
  comp varchar(16) default NULL,
  bytes int(11) default NULL,
  bytes_limit int(11) default NULL
) TYPE=MyISAM;

--
-- Table structure for table `transactions`
--

CREATE TABLE transactions (
  time timestamp(14) NOT NULL,
  admin varchar(255) NOT NULL default '',
  type varchar(255) NOT NULL default '',
  comp varchar(16) NOT NULL default '',
  bytes int(11) NOT NULL default '0',
  bytes_limit int(11) NOT NULL default '0'
) TYPE=MyISAM;

