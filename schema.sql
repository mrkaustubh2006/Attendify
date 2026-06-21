-- Database creation schema for MySQL (Production Environment)
-- Create Database if it does not exist
CREATE DATABASE IF NOT EXISTS `smart_attendance`;
USE `smart_attendance`;
-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` VARCHAR(20) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 2. Students Table
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `student_id` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `class_name` VARCHAR(100) NOT NULL,
    `roll_no` VARCHAR(50) NOT NULL,
    `qr_token` VARCHAR(100) NOT NULL UNIQUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_students_student_id` (`student_id`),
    INDEX `idx_students_qr_token` (`qr_token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 3. Teachers Table
CREATE TABLE IF NOT EXISTS `teachers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `teacher_id` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_teachers_teacher_id` (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 4. Subjects Table
CREATE TABLE IF NOT EXISTS `subjects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_name` VARCHAR(100) NOT NULL,
    `subject_code` VARCHAR(50) NOT NULL UNIQUE,
    INDEX `idx_subjects_subject_code` (`subject_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 5. Attendance Table
CREATE TABLE IF NOT EXISTS `attendance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `subject_id` INT NOT NULL,
    `date` DATE NOT NULL,
    `time` TIME NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Present',
    `attendance_method` VARCHAR(20) NOT NULL DEFAULT 'QR',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `_student_subject_date_uc` (`student_id`, `subject_id`, `date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 6. Active Sessions Table
CREATE TABLE IF NOT EXISTS `active_sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `teacher_id` INT NOT NULL,
    `subject_id` INT NOT NULL,
    `class_name` VARCHAR(100) NOT NULL,
    `token` VARCHAR(100) NOT NULL UNIQUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `expires_at` DATETIME NOT NULL,
    `is_active` TINYINT(1) DEFAULT 1,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE,
    INDEX `idx_sessions_token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
