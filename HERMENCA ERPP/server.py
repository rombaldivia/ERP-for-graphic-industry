import asyncio
from pymodbus.server.async_io import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification

async def run_async_modbus_server():
    # Crear el contexto de los datos Modbus
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*100),
        hr=ModbusSequentialDataBlock(0, [0]*100),
        ir=ModbusSequentialDataBlock(0, [0]*100)
    )
    context = ModbusServerContext(slaves=store, single=True)

    # Configurar la identificación del dispositivo
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Python Server'
    identity.ProductCode = 'PYSRV'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Python Modbus Server'
    identity.ModelName = 'Modbus Server'
    identity.MajorMinorRevision = '1.0'

    # Iniciar el servidor Modbus TCP de manera asíncrona
    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=("0.0.0.0", 502)
    )

if __name__ == "__main__":
    asyncio.run(run_async_modbus_server())
