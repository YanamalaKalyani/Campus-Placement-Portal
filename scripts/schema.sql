-- Campus Placement Portal Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS campus_placement;
USE campus_placement;

-- Users table (base table for all user types)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student', 'company') NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    enrollment_number VARCHAR(50) NOT NULL UNIQUE,
    branch VARCHAR(100) DEFAULT 'Not specified',
    semester INT DEFAULT 1,
    tenth DECIMAL(5,2) DEFAULT 0.00,
    twelfth DECIMAL(5,2) DEFAULT 0.00,
    cgpa DECIMAL(3,2) DEFAULT 0.00,
    backlogs INT DEFAULT 0,
    phone VARCHAR(20),
    skills TEXT,
    certifications TEXT,
    internship TEXT,
    projects TEXT,
    placement_status ENUM('unplaced', 'placed') DEFAULT 'unplaced',
    package_offered DECIMAL(10,2) DEFAULT 0.00,
    is_sample TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    contact VARCHAR(50),
    description TEXT,
    domain VARCHAR(100),
    package_lpa DECIMAL(10,2) DEFAULT 0.00,
    min_cgpa DECIMAL(3,2) DEFAULT 0.00,
    max_backlogs INT DEFAULT 0,
    position VARCHAR(255),
    required_skills VARCHAR(255),
    rounds INT DEFAULT 1,
    logo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Placement Drives table
CREATE TABLE IF NOT EXISTS placement_drives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    package DECIMAL(10,2) NOT NULL,
    eligibility_criteria TEXT,
    drive_date DATE,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    drive_id INT NOT NULL,
    status ENUM('pending', 'shortlisted', 'accepted', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (student_id, drive_id)
);

-- Placement Statistics Settings
CREATE TABLE IF NOT EXISTS placement_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_students INT DEFAULT 0,
    placed_students INT DEFAULT 0,
    avg_package DECIMAL(10,2) DEFAULT 0,
    highest_package DECIMAL(10,2) DEFAULT 0,
    lowest_package DECIMAL(10,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS placement_branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    branch VARCHAR(100) NOT NULL,
    total INT DEFAULT 0,
    placed INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS placement_yearly_package (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    avg_package DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    target_role ENUM('all', 'student', 'company', 'admin') DEFAULT 'all',
    user_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_students_branch ON students(branch);
CREATE INDEX idx_students_status ON students(placement_status);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_drives_status ON placement_drives(status);
CREATE INDEX idx_notifications_role ON notifications(target_role);

-- Insert sample admin user (password: admin123)
INSERT INTO users (email, password, role, name) VALUES 
('admin@campus.edu', 'pbkdf2:sha256:600000$LKYyXhVb$8d3e8a9f5c7b2d1e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e', 'admin', 'Super Admin');

INSERT INTO admins (user_id, name, email) VALUES 
(1, 'Super Admin', 'admin@campus.edu');

-- Insert sample students
INSERT INTO users (email, password, role, name) VALUES 
('priti@gmail.com', 'pbkdf2:sha256:600000$LKYyXhVb$8d3e8a9f5c7b2d1e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e', 'student', 'Priti Bhadja'),
('om@gmail.com', 'pbkdf2:sha256:600000$LKYyXhVb$8d3e8a9f5c7b2d1e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e', 'student', 'Om Panchal'),
('bhargi@gmail.com', 'pbkdf2:sha256:600000$LKYyXhVb$8d3e8a9f5c7b2d1e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e', 'student', 'Bhargi Antala');

INSERT INTO students (user_id, name, email, enrollment_number, branch, cgpa, phone, skills, placement_status, package_offered, is_sample) VALUES 
(2, 'Priti Bhadja', 'priti@gmail.com', 'EN12345678', 'CE', 8.00, '8347758215', 'Python, JavaScript, React', 'placed', 1800000, 1),
(3, 'Om Panchal', 'om@gmail.com', 'EN23456789', 'CSE', 7.50, '9876543210', 'Java, Spring Boot', 'unplaced', 0, 1),
(4, 'Bhargi Antala', 'bhargi@gmail.com', 'EN34567890', 'ECE', 8.20, '9876543211', 'C++, Embedded Systems', 'unplaced', 0, 1);

-- Insert sample company
INSERT INTO users (email, password, role, name) VALUES 
('google@company.com', 'pbkdf2:sha256:600000$LKYyXhVb$8d3e8a9f5c7b2d1e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e4f6a8c9b0d2e', 'company', 'Google');

INSERT INTO companies (user_id, name, email, description) VALUES 
(5, 'Google', 'google@company.com', 'Leading technology company specializing in Internet-related services and products.');

-- Insert sample placement drive
INSERT INTO placement_drives (company_id, title, description, package, eligibility_criteria, drive_date, status) VALUES 
(1, 'Software Engineer 2024', 'Full-time software engineer position', 1800000, 'CGPA >= 7.0, CSE/IT/ECE branches', '2024-03-15', 'active');

-- Insert sample notification
INSERT INTO notifications (title, message, target_role) VALUES 
('Welcome to Campus Portal', 'Welcome to the Campus Placement Portal. Start exploring opportunities!', 'all');
