-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 15, 2025 at 05:10 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `contacthub`
--

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

CREATE TABLE `contacts` (
  `contact_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `number` varchar(14) NOT NULL,
  `job_title` varchar(50) DEFAULT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `note` text DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Triggers `contacts`
--
DELIMITER $$
CREATE TRIGGER `after_contacts_delete` AFTER DELETE ON `contacts` FOR EACH ROW BEGIN
    INSERT INTO contacts_audit (contact_id, user_id, action_type, old_name, old_number, old_job_title)
    VALUES (OLD.contact_id, OLD.user_id, 'DELETE', OLD.name, OLD.number, OLD.job_title);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_contacts_insert` AFTER INSERT ON `contacts` FOR EACH ROW BEGIN
    INSERT INTO contacts_audit (contact_id, user_id, action_type, new_name, new_number, new_job_title)
    VALUES (NEW.contact_id, NEW.user_id, 'INSERT', NEW.name, NEW.number, NEW.job_title);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_contacts_update` AFTER UPDATE ON `contacts` FOR EACH ROW BEGIN
    INSERT INTO contacts_audit (contact_id, user_id, action_type, old_name, new_name, old_number, new_number, old_job_title, new_job_title)
    VALUES (OLD.contact_id, OLD.user_id, 'UPDATE', OLD.name, NEW.name, OLD.number, NEW.number, OLD.job_title, NEW.job_title);
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `contacts_audit`
--

CREATE TABLE `contacts_audit` (
  `audit_id` int(11) NOT NULL,
  `contact_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action_type` enum('INSERT','UPDATE','DELETE') DEFAULT NULL,
  `old_name` varchar(255) DEFAULT NULL,
  `new_name` varchar(255) DEFAULT NULL,
  `old_number` varchar(20) DEFAULT NULL,
  `new_number` varchar(20) DEFAULT NULL,
  `old_job_title` varchar(255) DEFAULT NULL,
  `new_job_title` varchar(255) DEFAULT NULL,
  `change_timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `date_created` date NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Triggers `users`
--
DELIMITER $$
CREATE TRIGGER `after_users_delete` AFTER DELETE ON `users` FOR EACH ROW BEGIN
    INSERT INTO users_audit (user_id, action_type, old_username, old_email)
    VALUES (OLD.user_id, 'DELETE', OLD.username, OLD.email);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_users_insert` AFTER INSERT ON `users` FOR EACH ROW BEGIN
    INSERT INTO users_audit (user_id, action_type, new_username, new_email)
    VALUES (NEW.user_id, 'INSERT', NEW.username, NEW.email);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_users_update` AFTER UPDATE ON `users` FOR EACH ROW BEGIN
    INSERT INTO users_audit (user_id, action_type, old_username, new_username, old_email, new_email)
    VALUES (OLD.user_id, 'UPDATE', OLD.username, NEW.username, OLD.email, NEW.email);
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `users_audit`
--

CREATE TABLE `users_audit` (
  `audit_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action_type` enum('INSERT','UPDATE','DELETE') DEFAULT NULL,
  `old_username` varchar(255) DEFAULT NULL,
  `new_username` varchar(255) DEFAULT NULL,
  `old_email` varchar(255) DEFAULT NULL,
  `new_email` varchar(255) DEFAULT NULL,
  `change_timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`contact_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `contacts_audit`
--
ALTER TABLE `contacts_audit`
  ADD PRIMARY KEY (`audit_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `users_audit`
--
ALTER TABLE `users_audit`
  ADD PRIMARY KEY (`audit_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `contact_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `contacts_audit`
--
ALTER TABLE `contacts_audit`
  MODIFY `audit_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users_audit`
--
ALTER TABLE `users_audit`
  MODIFY `audit_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `contacts`
--
ALTER TABLE `contacts`
  ADD CONSTRAINT `contacts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;