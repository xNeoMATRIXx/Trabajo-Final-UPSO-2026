-- =====================================================================
-- Schema: Portfolio Devs (MySQL)
-- Crea la BD y todas las tablas. Idempotente: puede ejecutarse varias veces.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS portfolio_dev
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE portfolio_dev;

-- Eliminar en orden inverso (respetando FKs) para empezar limpio.
DROP TABLE IF EXISTS proyecto_links;
DROP TABLE IF EXISTS proyecto_tecnologia;
DROP TABLE IF EXISTS proyecto_lenguaje;
DROP TABLE IF EXISTS proyectos;
DROP TABLE IF EXISTS habilidades;
DROP TABLE IF EXISTS usuarios;

-- ---------------------------------------------------------------------
-- usuarios
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  email           VARCHAR(190) NOT NULL UNIQUE,
  username        VARCHAR(30)  NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NOT NULL,
  nombre          VARCHAR(120) NULL,
  bio             TEXT NULL,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- habilidades: relación N:M usuarios ↔ tecnologías (catálogo hardcodeado)
-- ---------------------------------------------------------------------
CREATE TABLE habilidades (
  usuario_id     INT NOT NULL,
  tecnologia_id  INT NOT NULL,
  nivel          ENUM('basico', 'intermedio', 'avanzado') NOT NULL,
  PRIMARY KEY (usuario_id, tecnologia_id),
  CONSTRAINT fk_habilidades_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- proyectos
-- ---------------------------------------------------------------------
CREATE TABLE proyectos (
  id                     INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id             INT NOT NULL,
  nombre                 VARCHAR(160) NOT NULL,
  descripcion            TEXT NULL,
  etapa                  ENUM('formulacion','modelado','implementacion','testing','produccion','mantenimiento') NOT NULL,
  fecha_creacion         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  fecha_finalizacion     DATE NULL,
  fecha_deadline         DATE NULL,
  CONSTRAINT fk_proyectos_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios(id) ON DELETE CASCADE,
  INDEX idx_proyectos_usuario (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- proyecto_lenguaje: N:M proyectos ↔ lenguajes (catálogo hardcodeado)
-- ---------------------------------------------------------------------
CREATE TABLE proyecto_lenguaje (
  proyecto_id   INT NOT NULL,
  lenguaje_id   INT NOT NULL,
  PRIMARY KEY (proyecto_id, lenguaje_id),
  CONSTRAINT fk_proylen_proy FOREIGN KEY (proyecto_id)
    REFERENCES proyectos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- proyecto_tecnologia: N:M proyectos ↔ tecnologías (catálogo hardcodeado)
-- ---------------------------------------------------------------------
CREATE TABLE proyecto_tecnologia (
  proyecto_id    INT NOT NULL,
  tecnologia_id  INT NOT NULL,
  PRIMARY KEY (proyecto_id, tecnologia_id),
  CONSTRAINT fk_proytec_proy FOREIGN KEY (proyecto_id)
    REFERENCES proyectos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- proyecto_links: múltiples links por proyecto, pueden repetir tipo
-- ---------------------------------------------------------------------
CREATE TABLE proyecto_links (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  proyecto_id   INT NOT NULL,
  tipo          ENUM('repositorio','demo','documentacion','video','otro') NOT NULL,
  url           VARCHAR(500) NOT NULL,
  CONSTRAINT fk_proylinks_proy FOREIGN KEY (proyecto_id)
    REFERENCES proyectos(id) ON DELETE CASCADE,
  INDEX idx_proylinks_proy (proyecto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;