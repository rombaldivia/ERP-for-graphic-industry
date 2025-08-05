from pymodbus.client.tcp import ModbusTcpClient
import time

client = ModbusTcpClient('localhost', port=502)

client.connect()

try:
    while True:
        # Solicitar el valor a enviar mediante consola
        value_to_send = int(input("Introduce el valor a enviar: "))

        # Dirección del registro Modbus al que deseas escribirx 
        register_address = 0

        # Escribir el valor en el registro Modbus (escribe en un solo registro)
        client.write_register(register_address, value_to_send)

        # Leer el valor de retorno (opcional)
        response = client.read_holding_registers(register_address, 1)
        print(f"Valor enviado: {value_to_send}, Valor recibido: {response.registers[0]}")

        # Espera antes de enviar el siguiente valor (ajusta según sea necesario)
        time.sleep(1)

except KeyboardInterrupt:
    print("Proceso interrumpido por el usuario.")

finally:
    # Cerrar la conexión Modbus
    client.close()
