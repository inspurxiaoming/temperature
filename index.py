import serial #导入模块
import binascii
import MySQLdb
import datetime;  # 引入time模块
import time
import uuid
import logging
from logging.handlers import TimedRotatingFileHandler
logger = logging.getLogger('temperature-log')
logger.setLevel(logging.INFO)
ch = TimedRotatingFileHandler("temperature-log.log", when='D', encoding="utf-8")
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
def gettemperature():
    try:
      #端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
      portx="COM5"
      #波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
      bps=38400
      #超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
      timex=5
      # 打开串口，并得到串口对象
      ser=serial.Serial(portx,bps,timeout=timex)
      print("串口详情参数：", ser)

      print(ser.port)#获取到当前打开的串口名
      print(ser.baudrate)#获取波特率
      #循环接收数据，此为死循环，可用线程实现
      while True:
             if ser.in_waiting:
                 str=ser.read(ser.in_waiting ).hex()
                 if(str=="exit"):#退出标志
                     break
                 else:
                   # print("收到数据：",str)
                   strString=(binascii.a2b_hex(str)).strip()
                   # for value in strlist:  # 循环输出列表值
                   #     print(value)
                   node=((strString.decode()).split(' ', 1)[0].split(',',1)[0]).split('=',1)[1]
                   temperature=((strString.decode()).split(' ', 1)[0].split(',',1)[1]).split('=',1)[1]
                   setIntoDB((strString.decode()).split(' ', 1)[0],node,temperature)
                   print(datetime.datetime.now(),strString)
                   logger.info(strString.decode())
      print("---------------")
      ser.close()#关闭串口
    except Exception as e:
        print("---异常---：",e)
        logger.critical(e)
        ser.close()  # 关闭串口
    except :
        ser.close()
    finally:
        logger.info("------------重启服务------------")
        gettemperature()

def setIntoDB(str,node,temperature):
    # 打开数据库连接
    db = MySQLdb.connect("localhost", "root", "mylove093196", "temperature", charset='utf8')
    # db = MySQLdb.connect("192.168.0.129", "root", "mylove093196", "serverlist", charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    time_array = time.localtime(time.time())
    other_way_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    # SQL 插入语句
    sql = "INSERT INTO data_collection_temperature(id, \
           record, time,node,temperature) \
           VALUES ('%s', '%s', '%s', '%s', '%s')" % \
          (uuid.uuid1(), str, other_way_time,node,temperature)
    try:
        # 执行sql语句
        cursor.execute(sql)
        print("success")
        # 提交到数据库执行
        db.commit()
    except Exception as edb:
        # 发生错误时回滚
        print("error",edb)
        db.rollback()

    # 关闭数据库连接
    db.close()

gettemperature();