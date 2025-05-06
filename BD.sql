-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS `agenda_medica` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `agenda_medica`;

-- Tabla de doctores
CREATE TABLE `doctores` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `especialidad` VARCHAR(100) NOT NULL,
  `horario_disponible` LONGTEXT CHECK (json_valid(`horario_disponible`)),
  `activo` TINYINT(1) DEFAULT 1,
  `username` VARCHAR(50) UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de citas
CREATE TABLE `citas` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre_paciente` VARCHAR(100) NOT NULL,
  `carnet_paciente` VARCHAR(20) DEFAULT NULL CHECK (`carnet_paciente` REGEXP '^[0-9]+$'),
  `doctor_id` INT(11) NOT NULL,
  `fecha` DATE NOT NULL,
  `hora` TIME NOT NULL,
  `estado` ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'pendiente',
  PRIMARY KEY (`id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `citas_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Inserción de doctores con usuarios y contraseñas simples
INSERT INTO `doctores` (`nombre`, `especialidad`, `horario_disponible`, `activo`, `username`, `password`) VALUES
('Dr. Carlos Fernández', 'Cardiología', '{"Lunes": ["08:00", "16:00"], "Miércoles": ["09:00", "17:00"]}', 1, 'carlosf', 'password123'),
('Dra. Ana García', 'Pediatría', '{"Martes": ["08:00", "15:00"], "Jueves": ["10:00", "18:00"]}', 1, 'anag', 'password123'),
('Dra. Laura Méndez', 'Dermatología', '{"Lunes": ["08:00", "12:00"], "Miércoles": ["14:00", "18:00"], "Viernes": ["09:00", "13:00"]}', 1, 'lauram', 'password123'),
('Dr. Roberto Jiménez', 'Ortopedia', '{"Martes": ["07:30", "15:30"], "Jueves": ["08:00", "16:00"]}', 1, 'robertoj', 'password123'),
('Dra. Sofía Ramírez', 'Ginecología', '{"Lunes": ["09:00", "17:00"], "Miércoles": ["08:00", "16:00"]}', 1, 'sofiar', 'password123'),
('Dr. Ernesto Salinas', 'Neurología', '{"Martes": ["08:00", "14:00"], "Viernes": ["10:00", "16:00"]}', 1, 'ernestos', 'password123'),
('Dra. Camila Ortiz', 'Endocrinología', '{"Lunes": ["09:00", "15:00"], "Jueves": ["12:00", "18:00"]}', 1, 'camila', 'password123'),
('Dr. Andrés Molina', 'Urología', '{"Miércoles": ["07:30", "13:30"], "Viernes": ["09:00", "15:00"]}', 1, 'andresm', 'password123'),
('Dra. Patricia Guzmán', 'Oftalmología', '{"Martes": ["10:00", "16:00"], "Jueves": ["08:00", "14:00"]}', 1, 'patriciag', 'password123'),
('Dr. Diego Vargas', 'Gastroenterología', '{"Lunes": ["08:30", "13:30"], "Miércoles": ["10:00", "16:00"]}', 1, 'diegov', 'password123'),
('Dra. Isabel Rivas', 'Psicología', '{"Martes": ["09:00", "13:00"], "Viernes": ["08:00", "12:00"]}', 1, 'isabelr', 'password123'),
('Dr. Julio Herrera', 'Reumatología', '{"Lunes": ["10:00", "14:00"], "Jueves": ["13:00", "17:00"]}', 1, 'julioh', 'password123'),
('Dra. Valeria Paredes', 'Medicina Interna', '{"Miércoles": ["08:00", "12:00"], "Viernes": ["14:00", "18:00"]}', 1, 'valeriap', 'password123'),
('Dr. Álvaro Contreras', 'Nefrología', '{"Martes": ["08:00", "14:00"], "Jueves": ["09:00", "15:00"]}', 1, 'alvaroc', 'password123'),
('Dra. Fernanda Salcedo', 'Otorrinolaringología', '{"Lunes": ["07:30", "13:30"], "Miércoles": ["10:00", "16:00"]}', 1, 'fernandas', 'password123');

-- Inserción de citas
INSERT INTO `citas` (`nombre_paciente`, `carnet_paciente`, `doctor_id`, `fecha`, `hora`, `estado`) VALUES
('María González', '12345678', 1, '2025-04-15', '09:00:00', 'pendiente'),
('Juan Pérez', '87654321', 2, '2025-04-16', '10:30:00', 'pendiente'),
('Ana López', '11223344', 3, '2025-04-17', '11:00:00', 'pendiente'),
('Carlos Sánchez', '55667788', 4, '2025-04-18', '14:00:00', 'pendiente'),
('Laura Martínez', '99887766', 5, '2025-04-19', '15:30:00', 'pendiente'),
('Pedro Ramírez', '33445566', 1, '2025-04-20', '16:00:00', 'pendiente'),
('Sofía Herrera', '77889900', 2, '2025-04-21', '08:30:00', 'pendiente'),
('Miguel Díaz', '12121212', 3, '2025-04-22', '09:45:00', 'pendiente'),
('Elena Castro', '34343434', 4, '2025-04-23', '10:15:00', 'pendiente'),
('Jorge Navarro', '56565656', 5, '2025-04-24', '13:30:00', 'pendiente'),
('Luis Martínez', '90112233', 6, '2025-05-06', '08:30:00', 'pendiente'),
('Andrea Rojas', '77881122', 7, '2025-05-08', '12:30:00', 'pendiente'),
('Ricardo Soto', '44556677', 8, '2025-05-07', '10:15:00', 'pendiente'),
('Mónica Varela', '55667788', 9, '2025-05-13', '10:45:00', 'pendiente'),
('Gabriel Ruiz', '66778899', 10, '2025-05-06', '09:15:00', 'pendiente'),
('Natalia Guzmán', '77889911', 11, '2025-05-09', '10:00:00', 'pendiente'),
('Felipe Cordero', '88990022', 12, '2025-05-12', '11:00:00', 'pendiente'),
('Daniela Pérez', '33445566', 13, '2025-05-14', '09:00:00', 'pendiente'),
('Samuel Ortega', '22334455', 14, '2025-05-15', '10:30:00', 'pendiente'),
('Carmen Fuentes', '11223344', 15, '2025-05-19', '08:45:00', 'pendiente'),
('Esteban Salas', '99990000', 6, '2025-06-03', '11:00:00', 'pendiente'),
('Lina Castaño', '66665555', 7, '2025-06-06', '13:45:00', 'pendiente'),
('Rafael Méndez', '12121212', 8, '2025-06-04', '09:30:00', 'pendiente'),
('Melissa Jiménez', '34343434', 9, '2025-06-10', '11:15:00', 'pendiente'),
('Julián Torres', '98989898', 10, '2025-06-03', '12:00:00', 'pendiente'),
('Paola Alfaro', '67676767', 11, '2025-06-07', '08:30:00', 'pendiente'),
('Fernando Valverde', '12344321', 12, '2025-06-09', '13:30:00', 'pendiente'),
('Mariela Calderón', '45454545', 13, '2025-06-11', '10:00:00', 'pendiente'),
('Ismael Rivera', '56565656', 14, '2025-06-12', '09:15:00', 'pendiente'),
('Tamara Benítez', '21212121', 15, '2025-06-16', '11:30:00', 'pendiente');

-- Reinicio de AUTO_INCREMENT
ALTER TABLE `doctores` AUTO_INCREMENT = 10000;
ALTER TABLE `citas` AUTO_INCREMENT = 20000;