-- \i D:/Tesis/BDscript/tables.sql
DROP TABLE espway;
DROP TABLE espectros;
DROP TABLE espectros_referencia;
DROP TABLE sensores;
DROP TABLE waypoints;
DROP TABLE telemetria;
DROP TABLE mision;
DROP TABLE usuarios;

CREATE TABLE usuarios (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	nombre VARCHAR(50) UNIQUE NOT NULL , 
	contrasena VARCHAR(50) NOT NULL
);

CREATE TABLE mision (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	nombre VARCHAR(20) UNIQUE NOT NULL,
	elevacion DECIMAL NOT NULL,
	velocidad DECIMAL NOT NULL,
	modo_vuelo VARCHAR(1) NOT NULL,
	modo_adq VARCHAR(1) NOT NULL,
	usuarios_id BIGSERIAL NOT NULL REFERENCES usuarios(id)
);

CREATE TABLE telemetria (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	pitch DECIMAL NOT NULL,
	yaw DECIMAL NOT NULL,
	roll DECIMAL NOT NULL,
	lat DECIMAL NOT NULL,
	lon DECIMAL NOT NULL,
	alt DECIMAL NOT NULL,
	bateriaDron DECIMAL NOT NULL,
	velocidadDron VARCHAR(255) NOT NULL,
	mision_id BIGSERIAL NOT NULL REFERENCES mision(id) ON DELETE CASCADE
);

CREATE TABLE waypoints (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	num_waypoint DECIMAL NOT NULL,
	latlon VARCHAR(20) NOT NULL,
	mision_id BIGSERIAL NOT NULL REFERENCES mision(id) ON DELETE CASCADE
);

CREATE TABLE sensores (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	lugar VARCHAR(1) NOT NULL,
	tipo VARCHAR(1) NOT NULL,
	numero_serie VARCHAR(7) NOT NULL,
	t_int INT NOT NULL,
	numero_capt INT NOT NULL,
	mision_id BIGSERIAL NOT NULL REFERENCES mision(id) ON DELETE CASCADE
);

CREATE TABLE espectros (
	id BIGSERIAL NOT NULL PRIMARY KEY,
	white VARCHAR[],
	dark VARCHAR[],
	capturado VARCHAR[],
	resultado VARCHAR[],
	sensores_id BIGSERIAL NOT NULL REFERENCES sensores(id) ON DELETE CASCADE
);

-- CREATE TABLE espway (
-- 	espectros_id DECIMAL NOT NULL REFERENCES espectros(id)
-- 	waypoints_id DECIMAL UNIQUE NOT NULL REFERENCES waypoints(id)
-- 	CONSTRAINT espway_pkey PRIMARY KEY (espectros_id, waypoints_id) 
-- );

CREATE TABLE espway (
    espectros_id BIGSERIAL PRIMARY KEY,
    waypoints_id BIGSERIAL UNIQUE NOT NULL,
    CONSTRAINT espectros_fkey FOREIGN KEY (espectros_id) REFERENCES espectros(id) ON DELETE CASCADE,
    CONSTRAINT waypoints_fkey FOREIGN KEY (waypoints_id) REFERENCES waypoints(id) ON DELETE CASCADE
);

-- CREATE TABLE ref (
-- 	id BIGSERIAL NOT NULL PRIMARY KEY,
-- 	sensores_id BIGSERIAL REFERENCES sensores(id)
-- 	waypoints_id BIGSERIAL NOT NULL REFERENCES waypoints(id)
-- 	espectros_id BIGSERIAL NOT NULL REFERENCES espectros(id)
-- );
-- CREATE TABLE espectros (
-- 	id BIGSERIAL NOT NULL PRIMARY KEY,
-- 	capturado VARCHAR[],
-- 	resultado VARCHAR[],
-- 	espectros_referencia_id BIGSERIAL NOT NULL REFERENCES espectros_referencia(id)
-- );
-- CREATE TABLE espectros_resultado (
-- 	id BIGSERIAL NOT NULL PRIMARY KEY,
-- 	resultado VARCHAR[],
-- 	espectros_id BIGSERIAL NOT NULL REFERENCES espectros(id)
-- );

-- INSERT INTO usuarios (nombre, contraseña) VALUES ('Camilo', '1234');

-- INSERT INTO mision (nombre, elevacion, velocidad, modo_vuelo, modo_adq, usuarios_id) 
-- VALUES ('Mision1', '10', '10', 'A', 'A', '1');

-- INSERT INTO sensores (lugar, tipo, numero_serie, t_int, numero_capt, mision_id) 
-- VALUES ('T', 'V', 'S092921', '300', '5', '1');

-- INSERT INTO espectros (white) VALUES ('{{1,2,3},{4,5,6},{7,8,9}}');


-- INSERT INTO usuarios (nombre, contraseña) VALUES ('Karen Dayana', '1234');
-- INSERT INTO usuarios (nombre, contraseña) VALUES ('Matsu', '1234');

-- INSERT INTO mision (nombre, elevacion, velocidad, modo_vuelo, modo_adq, usuarios_id) 
-- VALUES ('Mision1', '10', '10', 'A', 'A', '1');
-- INSERT INTO mision (nombre, elevacion, velocidad, modo_vuelo, modo_adq, usuarios_id) 
-- VALUES ('Mision2', '10', '10', 'A', 'A', '2');
-- INSERT INTO mision (nombre, elevacion, velocidad, modo_vuelo, modo_adq, usuarios_id) 
-- VALUES ('Mision3', '10', '10', 'A', 'A', '1');