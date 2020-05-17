-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema mrcdb
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `mrcdb` ;

-- ------------------------------------------------------
-- Schema mrcdb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mrcdb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `mrcdb` ;

-- -----------------------------------------------------
-- Table `mrcdb`.`department_lookup`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mrcdb`.`department_lookup` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `token` VARCHAR(200) NOT NULL,
  `department` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `token` (`token` ASC) VISIBLE,
  UNIQUE INDEX `department` (`department` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `mrcdb`.`employee`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mrcdb`.`employee` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `token` VARCHAR(200) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `user_dept_FK` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `token` (`token` ASC) VISIBLE,
  INDEX `ix_employee_user_dept_FK` (`user_dept_FK` ASC) VISIBLE,
  CONSTRAINT `employee_ibfk_1`
    FOREIGN KEY (`user_dept_FK`)
    REFERENCES `mrcdb`.`department_lookup` (`token`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `mrcdb`.`manager`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mrcdb`.`manager` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `pass` VARCHAR(128) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `title` VARCHAR(50) NOT NULL,
  `description` VARCHAR(500) NULL DEFAULT NULL,
  `manager_dept_FK` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE,
  INDEX `ix_manager_manager_dept_FK` (`manager_dept_FK` ASC) VISIBLE,
  CONSTRAINT `manager_ibfk_1`
    FOREIGN KEY (`manager_dept_FK`)
    REFERENCES `mrcdb`.`department_lookup` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `mrcdb`.`plan`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mrcdb`.`plan` (
  `id` INT NOT NULL,
  `plan_name` VARCHAR(200) NOT NULL,
  `funding_amount` DECIMAL(12,2) NOT NULL,
  `plan_justification` VARCHAR(300) NOT NULL,
  `description` VARCHAR(300) NOT NULL,
  `start_date` DATETIME NOT NULL,
  `end_date` DATETIME NOT NULL,
  `source_fund` INT NOT NULL,
  `dest_fund` INT NOT NULL,
  `fund_individuals` TINYINT(1) NOT NULL,
  `control_name` VARCHAR(50) NULL DEFAULT NULL,
  `control_window` DATETIME NULL DEFAULT NULL,
  `amount_limit` DECIMAL(12,2) NULL DEFAULT NULL,
  `usage_limit` INT NULL DEFAULT NULL,
  `complete` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `plan_name` (`plan_name` ASC) VISIBLE,
  INDEX `source_fund` (`source_fund` ASC) VISIBLE,
  INDEX `dest_fund` (`dest_fund` ASC) VISIBLE,
  CONSTRAINT `plan_ibfk_1`
    FOREIGN KEY (`source_fund`)
    REFERENCES `mrcdb`.`department_lookup` (`id`),
  CONSTRAINT `plan_ibfk_2`
    FOREIGN KEY (`dest_fund`)
    REFERENCES `mrcdb`.`department_lookup` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `mrcdb`.`user_plan`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mrcdb`.`user_plan` (
  `user_FK` INT NOT NULL,
  `plan_FK` INT NOT NULL,
  PRIMARY KEY (`user_FK`, `plan_FK`),
  INDEX `plan_FK` (`plan_FK` ASC) VISIBLE,
  CONSTRAINT `user_plan_ibfk_1`
    FOREIGN KEY (`user_FK`)
    REFERENCES `mrcdb`.`employee` (`id`),
  CONSTRAINT `user_plan_ibfk_2`
    FOREIGN KEY (`plan_FK`)
    REFERENCES `mrcdb`.`plan` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
