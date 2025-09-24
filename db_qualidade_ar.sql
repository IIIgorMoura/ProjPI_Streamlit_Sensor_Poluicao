create database db_qualidade_ar;
use db_qualidade_ar;

CREATE TABLE tb_sensor (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    co2 DECIMAL(8,2),
    poeira1 DECIMAL(8,2),
    poeira2 DECIMAL(8,2),
    altitude DECIMAL(8,2),
    umidade DECIMAL(5,2),
    temperatura DECIMAL(5,2),
    pressao DECIMAL(8,2)
);

select * from tb_sensor;