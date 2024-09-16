-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 10, 2024 at 01:21 PM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smart_pantry_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `foodcategories`
--

CREATE TABLE `foodcategories` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(255) NOT NULL,
  `user_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `foodcategories`
--

INSERT INTO `foodcategories` (`category_id`, `category_name`, `user_id`) VALUES
(1, 'Uncategorized', NULL),
(2, 'Pantry', NULL),
(6, 'Fidge', NULL),
(7, 'Chicken', 4);

--
-- Triggers `foodcategories`
--
DELIMITER $$
CREATE TRIGGER `foodcategories_BEFORE_DELETE` BEFORE DELETE ON `foodcategories` FOR EACH ROW BEGIN
    UPDATE FoodInventory SET category_id = 1 WHERE category_id = OLD.category_id;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `foodimages`
--

CREATE TABLE `foodimages` (
  `image_id` int(11) NOT NULL,
  `food_id` int(11) NOT NULL,
  `image_path` text NOT NULL,
  `upload_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `foodimages`
--

INSERT INTO `foodimages` (`image_id`, `food_id`, `image_path`, `upload_date`) VALUES
(7, 28, 'img\\food_images\\veggie_oil.webp', '2023-11-07 08:14:34'),
(8, 2, 'img\\food_images\\resize.webp', '2023-11-07 09:06:19'),
(9, 17, 'img\\food_images\\tomatopaste.webp', '2023-11-07 13:25:13'),
(10, 1, 'img\\food_images\\snicker_bar.jpg', '2023-11-07 13:59:41'),
(11, 4, 'img\\food_images\\farm_pride_egg.webp', '2023-11-08 17:12:10'),
(12, 5, 'img\\food_images\\veggie_oil.webp', '2023-11-09 00:08:39'),
(13, 15, 'img\\food_images\\resize.webp', '2023-11-09 07:58:42');

-- --------------------------------------------------------

--
-- Table structure for table `foodinventory`
--

CREATE TABLE `foodinventory` (
  `food_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `food_name` varchar(255) NOT NULL,
  `purchase_date` date DEFAULT NULL,
  `expiration_date` date DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `memo` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `foodinventory`
--

INSERT INTO `foodinventory` (`food_id`, `user_id`, `category_id`, `food_name`, `purchase_date`, `expiration_date`, `quantity`, `memo`, `status`) VALUES
(1, 1, 1, 'Snickers Bar', '0000-00-00', '2023-11-30', 2, '', NULL),
(2, 1, 1, 'Milo Beverage', '0000-00-00', '2023-12-13', 1, '', NULL),
(4, 1, 2, 'Farm Pride Large Eggs', '0000-00-00', '2023-11-11', 1, '', NULL),
(5, 1, 2, 'Great Value Milk', '0000-00-00', '2023-11-10', 5, '', NULL),
(15, 1, 2, 'Great Value Chocolate', '0000-00-00', '2023-11-09', 15, '', NULL),
(17, 1, 1, 'Tomato Paste', '0000-00-00', '2023-11-17', 20, '', NULL),
(28, 1, 2, 'Vegetable Oil', '2023-11-07', '2023-11-10', 6, '', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `notification_date` datetime NOT NULL DEFAULT current_timestamp(),
  `status` enum('Read','Unread') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sharedfood`
--

CREATE TABLE `sharedfood` (
  `share_id` int(11) NOT NULL,
  `food_id` int(11) NOT NULL,
  `sharing_date` datetime DEFAULT current_timestamp(),
  `expiry_for_sharing` date DEFAULT NULL,
  `status` enum('Available','Claimed','Shared') NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sharedfood`
--

INSERT INTO `sharedfood` (`share_id`, `food_id`, `sharing_date`, `expiry_for_sharing`, `status`, `title`, `description`, `quantity`) VALUES
(1, 17, '2023-11-10 05:28:25', NULL, 'Shared', 'Tomato Paste available for pickup', 'Almost expired tomato paste for quick pickup', 12),
(2, 17, '2023-11-10 05:29:08', NULL, 'Shared', 'Tomato Paste available for pickup #2', 'Almost expired tomato paste for quick pickup', 8);

-- --------------------------------------------------------

--
-- Table structure for table `sharedfoodclaims`
--

CREATE TABLE `sharedfoodclaims` (
  `claim_id` int(11) NOT NULL,
  `share_id` int(11) NOT NULL,
  `claimer_user_id` int(11) NOT NULL,
  `claim_date` datetime DEFAULT current_timestamp(),
  `claimfoodstatus` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `date_joined` datetime NOT NULL DEFAULT current_timestamp(),
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`, `email`, `first_name`, `last_name`, `date_joined`, `address`, `city`, `state`, `zip_code`) VALUES
(1, 'kel123', 'sha256$7FZlp4UaRJo0AMwf$610584299692b8254c5892649dca7213146d2672ec414760bae2e8a977f3be60', 'kelitembiz@gmail.com', 'Kelvin', 'Itemuagbor', '2023-09-27 01:57:12', '702 Santee Street, #2301', 'Prairie View', 'Texas', '77446'),
(3, 'ade12', 'sha256$z7GpWLJHedw7g0iU$c011beeedb0d55c610d18cb688bef89678a3ad6f1ef67c5c36127eba07a8d903', 'k@g.com', 'adekunle', 'looius', '2023-09-27 22:40:56', '102 str', 'Houston', 'Texas', '77556'),
(4, 'JohnDoe', 'scrypt:32768:8:1$g0DL8lNDM6ExrHuG$245e5c957c0c54ea7bb85bf645816f56a22b44ca48867ab2f41b05f38da90f9340fa5824be62f9da71c30fbb5ef2ce2d295a15181c3f853f2ce3fde36c91fb50', 'xyz@gmail.com', 'Kelvin', 'Muindi', '2024-05-10 11:09:13', 'Nairobi', 'Nairobi', 'Kenya', '30159');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `foodcategories`
--
ALTER TABLE `foodcategories`
  ADD PRIMARY KEY (`category_id`);

--
-- Indexes for table `foodimages`
--
ALTER TABLE `foodimages`
  ADD PRIMARY KEY (`image_id`),
  ADD KEY `food_id` (`food_id`);

--
-- Indexes for table `foodinventory`
--
ALTER TABLE `foodinventory`
  ADD PRIMARY KEY (`food_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `sharedfood`
--
ALTER TABLE `sharedfood`
  ADD PRIMARY KEY (`share_id`),
  ADD KEY `food_id` (`food_id`);

--
-- Indexes for table `sharedfoodclaims`
--
ALTER TABLE `sharedfoodclaims`
  ADD PRIMARY KEY (`claim_id`),
  ADD KEY `share_id` (`share_id`),
  ADD KEY `claimer_user_id` (`claimer_user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `foodcategories`
--
ALTER TABLE `foodcategories`
  MODIFY `category_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `foodimages`
--
ALTER TABLE `foodimages`
  MODIFY `image_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `foodinventory`
--
ALTER TABLE `foodinventory`
  MODIFY `food_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sharedfood`
--
ALTER TABLE `sharedfood`
  MODIFY `share_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `sharedfoodclaims`
--
ALTER TABLE `sharedfoodclaims`
  MODIFY `claim_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `foodimages`
--
ALTER TABLE `foodimages`
  ADD CONSTRAINT `foodimages_ibfk_1` FOREIGN KEY (`food_id`) REFERENCES `foodinventory` (`food_id`);

--
-- Constraints for table `foodinventory`
--
ALTER TABLE `foodinventory`
  ADD CONSTRAINT `foodinventory_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `foodinventory_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `foodcategories` (`category_id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `sharedfood`
--
ALTER TABLE `sharedfood`
  ADD CONSTRAINT `sharedfood_ibfk_1` FOREIGN KEY (`food_id`) REFERENCES `foodinventory` (`food_id`);

--
-- Constraints for table `sharedfoodclaims`
--
ALTER TABLE `sharedfoodclaims`
  ADD CONSTRAINT `sharedfoodclaims_ibfk_1` FOREIGN KEY (`share_id`) REFERENCES `sharedfood` (`share_id`),
  ADD CONSTRAINT `sharedfoodclaims_ibfk_2` FOREIGN KEY (`claimer_user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
