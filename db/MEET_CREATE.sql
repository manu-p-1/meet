-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE =
        'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema meetdb
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `meetdb`;

-- -----------------------------------------------------
-- Schema meetdb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `meetdb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `meetdb`;

-- -----------------------------------------------------
-- Table `meetdb`.`department_lookup`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meetdb`.`department_lookup`
(
    `id`         INT          NOT NULL AUTO_INCREMENT,
    `token`      VARCHAR(200) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `department_UNIQUE` (`department` ASC) VISIBLE,
    UNIQUE INDEX `token_UNIQUE` (`token` ASC) VISIBLE
)
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb4
    COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `meetdb`.`employee`
-- -----------------------------------------------------
CREATE TABLE `meetdb`.`employee`
(
    `id`               int          NOT NULL AUTO_INCREMENT,
    `token`            varchar(50)  NOT NULL,
    `first_name`       varchar(45)  NOT NULL,
    `last_name`        varchar(45)  NOT NULL,
    `employee_dept_FK` varchar(200) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `token_UNIQUE` (`token`),
    KEY `employee_dept_FK_idx` (`employee_dept_FK`),
    CONSTRAINT `employee_dept_FK` FOREIGN KEY (`employee_dept_FK`) REFERENCES `department_lookup` (`token`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `meetdb`.`plan`
-- -----------------------------------------------------
CREATE TABLE `meetdb`.`plan`
(
    `id`                 int            NOT NULL AUTO_INCREMENT,
    `plan_name`          varchar(200)   NOT NULL,
    `funding_amount`     decimal(12, 2) NOT NULL,
    `plan_justification` varchar(50)    NOT NULL,
    `memo`               varchar(255)   NOT NULL,
    `start_date`         datetime       NOT NULL,
    `end_date`           datetime                DEFAULT NULL,
    `source_fund_FK`     int            NOT NULL,
    `dest_fund_FK`       int            NOT NULL,
    `fund_individuals`   bit(1)         NOT NULL DEFAULT b'0',
    `fund_all_employees` bit(1)         NOT NULL,
    `control_name`       varchar(50)             DEFAULT NULL,
    `control_window`     varchar(30)             DEFAULT NULL,
    `amount_limit`       decimal(12, 2)          DEFAULT NULL,
    `usage_limit`        int                     DEFAULT NULL,
    `priority`           varchar(45)    NOT NULL,
    `complete`           bit(1)         NOT NULL DEFAULT b'0',
    PRIMARY KEY (`id`),
    UNIQUE KEY `plan_name_UNIQUE` (`plan_name`),
    KEY `dest_fund_FK_idx` (`source_fund_FK`, `dest_fund_FK`),
    KEY `dest_fund_FK_idx1` (`dest_fund_FK`),
    CONSTRAINT `dest_fund_FK` FOREIGN KEY (`dest_fund_FK`) REFERENCES `department_lookup` (`id`),
    CONSTRAINT `source_fund_FK` FOREIGN KEY (`source_fund_FK`) REFERENCES `department_lookup` (`id`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 23
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `meetdb`.`employee_plan`
-- -----------------------------------------------------
CREATE TABLE `meetdb`.`employee_plan`
(
    `ep_employee_FK` int NOT NULL,
    `ep_plan_FK`     int NOT NULL,
    `ep_card_token`  varchar(50) DEFAULT NULL,
    PRIMARY KEY (`ep_employee_FK`, `ep_plan_FK`),
    UNIQUE KEY `ep_card_token_UNIQUE` (`ep_card_token`),
    KEY `ep_plan_FK_idx` (`ep_plan_FK`),
    CONSTRAINT `ep_employee_FK` FOREIGN KEY (`ep_employee_FK`) REFERENCES `employee` (`id`),
    CONSTRAINT `ep_plan_FK` FOREIGN KEY (`ep_plan_FK`) REFERENCES `plan` (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------
-- Table `meetdb`.`manager`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `meetdb`.`manager`
(
    `id`              INT          NOT NULL AUTO_INCREMENT,
    `email`           VARCHAR(255) NOT NULL,
    `pass`            VARCHAR(128) NOT NULL,
    `first_name`      VARCHAR(45)  NOT NULL,
    `last_name`       VARCHAR(45)  NOT NULL,
    `gender`          VARCHAR(45)  NOT NULL,
    `title`           VARCHAR(50)  NOT NULL,
    `description`     VARCHAR(500) NULL DEFAULT NULL,
    `manager_dept_FK` INT          NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,
    INDEX `manager_dept_FK_idx` (`manager_dept_FK` ASC) VISIBLE,
    CONSTRAINT `manager_dept_FK`
        FOREIGN KEY (`manager_dept_FK`)
            REFERENCES `meetdb`.`department_lookup` (`id`)
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;


CREATE TABLE `meetdb`.`transaction`
(
    `id`                int            NOT NULL AUTO_INCREMENT,
    `src_token`         varchar(50)    NOT NULL,
    `dest_token`        varchar(50)    NOT NULL,
    `create_time`       datetime       NOT NULL,
    `amount`            decimal(12, 2) NOT NULL,
    `src_token_is_card` bit(1) DEFAULT b'0',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE `meetdb`.`employee_card`
(
    `ec_employee_token` varchar(50) NOT NULL,
    `ec_card_token`     varchar(50) NOT NULL,
    PRIMARY KEY (`ec_employee_token`, `ec_card_token`),
    CONSTRAINT `ec_employee_token` FOREIGN KEY (`ec_employee_token`) REFERENCES `employee` (`token`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;



INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To England', 1400, 'Travel', 'This is a travel plan', "2019-11-25 23:20:20", "2019-11-29 23:20:20", 1,
        1, 1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To China', 1600, 'Travel', 'This is a travel plan', "2019-11-21 05:20:20", "2020-01-29 05:20:20", 2, 2,
        1, 0, "Low", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees,  priority, complete)
VALUES ('Travel To Taiwan', 2250, 'Travel', 'This is a travel plan', "2019-12-25 23:20:20", "2019-12-29 23:20:20", 1, 1,
        1, 0, "Medium", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To India', 3256, 'Travel', 'This is a travel plan', "2019-12-21 05:20:20", "2019-12-29 05:20:20", 2, 2,
        1, 0, "Low", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Dallas', 500, 'Travel', 'This is a travel plan', "2020-01-20 23:20:20", "2020-01-22 23:20:20", 7, 7,
        1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Los Angeles', 500, 'Travel', 'This is a travel plan', "2020-01-04 05:20:20", "2020-01-15 05:20:20",
        3, 3, 1, 0, "Low", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Nantucket', 500, 'Travel', 'This is a travel plan', "2020-01-20 23:20:20", "2020-01-22 23:20:20", 2,
        2,
        1, 0, "Medium", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To New Jersey', 2410, 'Travel', 'This is a travel plan', "2020-02-20 23:20:20", "2020-02-22 23:20:20",
        2,
        2,
        1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Austin', 500, 'Travel', 'This is a travel plan', "2020-01-04 05:20:20", "2020-01-15 05:20:20",
        2, 2, 1, 0, "Low", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To New York', 400, 'Travel', 'This is a travel plan', "2020-02-05 05:20:20", "2020-01-15 05:20:20", 5,
        5, 1, 0, "Medium", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Atlanta', 800, 'Travel', 'This is a travel plan', "2020-02-15 05:20:20", "2020-02-29 05:20:20", 5, 5,
        1, 0, "Low", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Salt Lake City', 400, 'Travel', 'This is a travel plan', "2020-03-15 05:20:20",
        "2020-03-29 05:20:20", 5, 5, 1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Chicago', 1235, 'Travel', 'This is a travel plan', "2020-03-20 05:20:20", "2020-03-25 05:20:20", 2,
        2, 1, 0, "High", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Montgomery', 400, 'Travel', 'This is a travel plan', "2020-03-15 05:20:20",
        "2020-03-29 05:20:20", 2, 2, 1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Miami', 2654, 'Travel', 'This is a travel plan', "2020-03-20 05:20:20", "2020-03-25 05:20:20", 2,
        2, 1, 0, "Urgent", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Charleston', 400, 'Travel', 'This is a travel plan', "2020-03-16 05:20:20", "2020-03-29 05:20:20", 5,
        5, 1, 0, "Urgent", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Indianapolis', 1235, 'Travel', 'This is a travel plan', "2020-03-16 05:20:20", "2020-03-25 05:20:20",
        2, 2, 1, 0, "Low", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Seattle', 1000, 'Travel', 'This is a travel plan', "2020-04-12 05:20:20", "2020-04-12 23:20:20", 4,
        4, 1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Omaha', 1000, 'Travel', 'This is a travel plan', "2020-04-13 05:20:20", "2020-04-17 23:20:20", 4, 4,
        1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Phoenix', 1100, 'Travel', 'This is a travel plan', "2020-04-20 23:20:20", "2020-04-22 23:20:20", 2,
        2,
        1, 0, "Medium", 1);


INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Tacoma', 1000, 'Travel', 'This is a travel plan', "2020-05-12 05:20:20", "2020-05-12 23:20:20", 1, 1,
        1, 0, "Low", 1);

INSERT INTO plan(plan_name, funding_amount, plan_justification, memo, start_date, end_date, source_fund_FK,
                 dest_fund_FK, fund_individuals, fund_all_employees, priority, complete)
VALUES ('Travel To Rio', 2541, 'Travel', 'This is a travel plan', "2020-05-13 05:20:20", "2020-05-17 23:20:20", 1, 1, 1,
        0, "Low", 1);