import socket
import configparser
import pyttsx3
import time

config = configparser.ConfigParser()
config.read('client_config.ini')

engine = pyttsx3.init()

host = socket.gethostname()
# host = '172.20.202.151'
port = 1241

def voice(phrase):
    engine.setProperty("rate", 100)
    engine.say(phrase)
    engine.runAndWait()

def decode_message(msg):
    msg_split = (msg).split(",")
    for comp_msg in msg_split:
        comp_msg_split = comp_msg.split("=")
        try:
            comp_short_code = comp_msg_split[0]
            now_status = comp_msg_split[1]
            early_status = config[comp_short_code]['status']
            if early_status == '0' and now_status == '1':
                print("Anlayzer Started")
                name = config[comp_short_code]['name']
                phrase = f"{name} is Started"
                voice(phrase)

            elif early_status == '1' and now_status == '0':
                print("Anlayzer Down")
                name = config[comp_short_code]['name']
                phrase = f"{name} is Down Please check"
                voice(phrase)

            # config[comp_short_code]['early_status'] = config[comp_short_code]['now_status']
            config[comp_short_code]['status'] = now_status
            with open('temp.tmp', 'w') as configfile:
                config.write(configfile)
                configfile.close()
        except Exception as e:
            print(e)


class client:
    def __init__(self):
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Waiting for connection')
        try:
            ClientSocket.connect((host, port))
        except socket.error as e:
            print(str(e))
        self.ClientSocket = ClientSocket
        

        for section_name in config.sections():
            ip = config[section_name]['ip']
            name = config[section_name]['name']
            config[section_name] = {'ip': ip, 'name': name, 'status': '2'}
            with open('temp.tmp', 'w+') as configfile:
                config.write(configfile)
                configfile.close()
        
    # Response = ClientSocket.recv(2048)
    def getmsg(self):
        Response = self.ClientSocket.recv(2048)
        msg = Response.decode('utf-8')
        decode_message(msg)
        return msg
        self.ClientSocket.close()
c= client()
while True:
    print(c.getmsg())
    time.sleep(1)