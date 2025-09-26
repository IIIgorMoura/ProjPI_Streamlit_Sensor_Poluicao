# PERMITE A CONEXÃO DA API COM O BANCO DE DADOS
from flask import Flask, Response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

app = Flask('Sensores')

# RASTREIA AS MODIFICAÇÕES REALIZADAS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# CONFIGURAÇÃO DE CONEXÃO COM O BANCO (ajuste o nome do banco se necessário)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://grupo1DataScience:Senai%40134@db-sensor-datascience-senai-gp1.mysql.database.azure.com/db_qualidade_ar'

server_name = 'db-sensor-datascience-senai-gp1.mysql.database.azure.com'
port='3306'
username='grupo1DataScience'
password = 'Senai%40134'
database = 'db_qualidade_ar'

certificado = 'DigiCertGlobalRootG2.crt.pem'


# >>>>>>>>>>>>>>>>> Projeto do GRUPO 1: grupo1DataScience <<<<<<<<<<<<<<<<<<<<< 
uri = f"mysql+pymysql://{username}:{password}@{server_name}:{port}/{database}"
ssl_certificado = f'?ssl_ca={certificado}'

app.config['SQLALCHEMY_DATABASE_URI'] = uri + ssl_certificado

mybd = SQLAlchemy(app)
# ********************* CONEXÃO SENSORES *********************************
# pip install paho-mqtt

mqtt_data = {}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("projeto_integrado/SENAI134/Cienciadedados/grupo1")

def on_message(client, userdata, msg):
    global mqtt_data
 # Decodifica a mensagem recebida de bytes para string
    payload = msg.payload.decode('utf-8')
   
    # Converte a string JSON em um dicionário Python
    mqtt_data = json.loads(payload)
   
    # Imprime a mensagem recebida
    print(f"Received message: {mqtt_data}")

    # Adiciona o contexto da aplicação para a manipulação do banco de dados
    with app.app_context():
        try:
            temperatura = mqtt_data.get('temperature')
            pressao = mqtt_data.get('pressure')
            altitude = mqtt_data.get('altitude')
            umidade = mqtt_data.get('humidity'),
            # poeira1 = poeira1.get('particula1'),
            # poeira2 = poeira2.get('particula2'),
            co2 = mqtt_data.get('co2')
            timestamp_unix = mqtt_data.get('timestamp')

            if timestamp_unix is None:
                print("Timestamp não encontrado no payload")
                return

            # Converte timestamp Unix para datetime
            try:
                timestamp = datetime.fromtimestamp(int(timestamp_unix), tz=timezone.utc)
            except (ValueError, TypeError) as e:
                print(f"Erro ao converter timestamp: {str(e)}")
                return

            # Cria o objeto Registro com os dados
            new_data = Sensor(
                temperatura=temperatura,
                pressao=pressao,
                altitude=altitude,
                umidade=umidade,
                # poeira1=poeira1,
                # poeira2=poeira2,
                co2=co2,
                data_hora=timestamp
            )

            # Adiciona o novo registro ao banco de dados
            mybd.session.add(new_data)
            mybd.session.commit()
            print("Dados inseridos no banco de dados com sucesso")

        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mybd.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()






# CLASSE PARA DEFINIR O MODELO DOS DADOS QUE CORRESPONDE À TABELA DO BANCO DE DADOS
from sqlalchemy.sql import func # Importar 'func'

class Sensor(mybd.Model):
    __tablename__ = 'tb_sensor'
    id_registro = mybd.Column(mybd.Integer, primary_key=True)
    data_hora = mybd.Column(mybd.TIMESTAMP, nullable=False, server_default=func.now())
    co2 = mybd.Column(mybd.Numeric(8, 2))
    # poeira1 = mybd.Column(mybd.Numeric(8, 2))
    # poeira2 = mybd.Column(mybd.Numeric(8, 2))
    altitude = mybd.Column(mybd.Numeric(8, 2))
    umidade = mybd.Column(mybd.Numeric(5, 2))
    temperatura = mybd.Column(mybd.Numeric(5, 2))
    pressao = mybd.Column(mybd.Numeric(8, 2))

    # ESSE METODO to_json VAI SER USADO PARA CONVERTER O OBJETO EM JSON
    def to_json(self):
        return {
            "id_registro": self.id_registro,
            "data_hora": self.data_hora.isoformat() if self.data_hora else None,
            "co2": float(self.co2) if self.co2 is not None else None,
            "poeira1": float(self.poeira1) if self.poeira1 is not None else None,
            "poeira2": float(self.poeira2) if self.poeira2 is not None else None,
            "altitude": float(self.altitude) if self.altitude is not None else None,
            "umidade": float(self.umidade) if self.umidade is not None else None,
            "temperatura": float(self.temperatura) if self.temperatura is not None else None,
            "pressao": float(self.pressao) if self.pressao is not None else None,
        }

# ------------------------------------------------
# METODO 1 = GET ALL
@app.route('/sensores', methods=['GET'])
def seleciona_registros():
    registros_selecionados = Sensor.query.all()
    # EXECUTA UMA CONSULTA NO BANCO DE DADOS
    registros_json = [registro.to_json() for registro in registros_selecionados]
    
    return gera_resposta(200, "Sensores", registros_json)

# METODO 2 = GET BY ID
@app.route('/sensores/<id_registro_pam>', methods=['GET'])
def seleciona_registro_id(id_registro_pam):
    registro_selecionado = Sensor.query.filter_by(id_registro=id_registro_pam).first()
    registro_json = registro_selecionado.to_json()
    return gera_resposta(200, registro_json, 'Sensor encontrado!')

# METODO 3 - POST
@app.route('/sensores', methods=['POST'])
def criar_registro():
    requisicao = request.get_json()
    
    try:
        # id_registro não é incluído pois é AUTO_INCREMENT
        registro = Sensor(
            data_hora=requisicao['data_hora'],
            co2=requisicao['co2'],
            # poeira1=requisicao['poeira1'],
            # poeira2=requisicao['poeira2'],
            altitude=requisicao['altitude'],
            umidade=requisicao['umidade'],
            poeira1=requisicao['poeira1'],
            poeira2=requisicao['poeira2'],
            temperatura=requisicao['temperatura'],
            pressao=requisicao['pressao']
        )
        mybd.session.add(registro)
        # ADICIONA AO BANCO
        mybd.session.commit()
        # SALVA
    
        return gera_resposta(201, registro.to_json(), 'Criado com sucesso!')

    except Exception as e:
        print('erro', e)
        return gera_resposta(400, {}, "Erro ao cadastrar!")

# METODO 4 - DELETE
@app.route('/sensores/<id_registro_pam>', methods=['DELETE'])
def deleta_registro(id_registro_pam):
    registro = Sensor.query.filter_by(id_registro=id_registro_pam).first()
    
    try:
        mybd.session.delete(registro)
        mybd.session.commit()
        return gera_resposta(200, registro.to_json(), 'Deletado com sucesso!')

    except Exception as e:
        print('erro', e)
        return gera_resposta(400, {}, 'Erro ao deletar!')

# METODO 5- UPDATE
@app.route('/sensores/<id_registro_pam>', methods=['PUT'])
def atualiza_registro(id_registro_pam):
    registro = Sensor.query.filter_by(id_registro=id_registro_pam).first()
    requisicao = request.get_json()
    
    try:
        if('data_hora' in requisicao):
            registro.data_hora = requisicao['data_hora']
        if('co2' in requisicao):
            registro.co2 = requisicao['co2']
        if('poeira1' in requisicao):
            registro.poeira1 = requisicao['poeira1']
        if('poeira2' in requisicao):
            registro.poeira2 = requisicao['poeira2']
        if('altitude' in requisicao):
            registro.altitude = requisicao['altitude']
        if('umidade' in requisicao):
            registro.umidade = requisicao['umidade']
        if('temperatura' in requisicao):
            registro.temperatura = requisicao['temperatura']
        if('pressao' in requisicao):
            registro.pressao = requisicao['pressao']
            
        mybd.session.add(registro)
        mybd.session.commit()
        
        return gera_resposta(200, registro.to_json(), "Sensor atualizado com sucesso")
    
    except Exception as e:
        print('erro', e)
        return gera_resposta(400, {}, 'Erro ao atualizar!')
# --------------------------------------
# RESPOSTA PADRÃO
def gera_resposta(status, conteudo, mensagem=False):
    body = {}
    body['Registro Sensor'] = conteudo
    if(mensagem):
        body['Registros'] = mensagem
            
    return Response(json.dumps(body), status=status, mimetype='application/json')
    
# DUMPS - CONVERTE O DICIONÁRIO CRIADO (BODY) EM JSON
if __name__ == '__main__':
    with app.app_context():
        mybd.create_all()  # Cria as tabelas no banco de dados
   
    start_mqtt()
    app.run(port=5000, host='localhost', debug=True)
    