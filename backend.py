from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import pymysql

def connect_db():
    return pymysql.connect(host="localhost",
                           user="user",
                           password="strong_password",
                           db="mydb")

# Функция для SELECT запроса, принимает query строку и возвращает результат полученный из бд.
def db_select(query):
    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            # Выполнение команды запроса.
            cursor.execute(query)
            parts_sql_result = cursor.fetchall()

            # Конверируем [[1], [2]] -> [1, 2]
            result = []
            for part in parts_sql_result:
                result.append(part[0])
    finally:
        # Закрываем соединение.
        connection.close()

    return result

# Запросы в бд. Для каждого элемента конфигурации отдельная таблица, так как
# каждый элемент может иметь уникальные свойства, которых нет у других элементов.
def get_motherboards():
    return db_select("SELECT name FROM motherboards WHERE state='available'")

def get_cpus():
    return db_select("SELECT name FROM cpus WHERE state='available'")

def get_mems():
    return db_select("SELECT name FROM mems WHERE state='available'")

def get_hds():
    return db_select("SELECT name FROM hds WHERE state='available'")

def get_gpus():
    return db_select("SELECT name FROM gpus WHERE state='available'")

def get_powers():
    return db_select("SELECT name FROM powers WHERE state='available'")

def get_cases():
    return db_select("SELECT name FROM cases WHERE state='available'")

def insert_order(name, description, motherboard, cpu, mem, hd, gpu, power, case):
    # Формируем список элементов конфигурации для бд из аргументов функции
    values = ', '.join(str('"' + x + '"') for x in locals().values())
    # Формируем sql-запрос вставляющий сформированную конфигурацию в таблицу с заказами.
    query_insert_order = "INSERT INTO orders (order_time, name, description, motherboard, cpu, mem, hd, gpu, power, pc_case) VALUES (NOW(), " + values + ")"
    # Формируем sql-запрос увеличивающий количество заказов для сборщика у которого меньше всего заказов. Таблица должна иметь значение orders_num по умолчанию 0.
    query_add_order_to_builder = "UPDATE builders SET orders_num = orders_num + 1 WHERE id = (SELECT id FROM (SELECT id FROM builders ORDER BY orders_num ASC LIMIT 1) AS t)"
    # Формируем sql-запрос увеличивающий статистику заказов в определенный день.
    query_increase_orders_num = "INSERT INTO statistics (day, ordered) VALUES (NOW(), 1) ON DUPLICATE KEY UPDATE ordered = ordered + 1;"
    # Создаем подключение к бд.
    connection = connect_db()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query_insert_order)
            cursor.execute(query_add_order_to_builder)
            cursor.execute(query_increase_orders_num)
            connection.commit()

    finally:
        connection.close()

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        # Без этого хедера не работает с фронтом.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        options = {
            "motherboard": get_motherboards(),
            "cpu": get_cpus(),
            "mem": get_mems(),
            "hd": get_hds(),
            "gpu": get_gpus(),
            "power": get_powers(),
            "case": get_cases(),
        }

        options_json = json.dumps(options)
        self.wfile.write(str.encode(options_json))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        # Без этого хедера не работает с фронтом.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        o = json.loads(body)
        insert_order(o["name"], o["description"], o["motherboard"], o["cpu"], o["mem"], o["hd"], o["gpu"], o["power"], o["case"])

httpd = HTTPServer(('localhost', 9099), HTTPRequestHandler)
httpd.serve_forever()
