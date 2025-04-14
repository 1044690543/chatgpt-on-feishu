import json
import psycopg2
import requests
from decimal import Decimal
from bridge.reply import Reply, ReplyType
from config import conf, load_config

with open("config.json", "r", encoding="utf-8") as file:
    config_data = json.load(file)

sql_user = config_data.get("sql_user")
sql_password = config_data.get("sql_password")
sql_host = config_data.get("sql_host")
sql_port = config_data.get("sql_port")
sql_database = config_data.get("sql_database")

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    else:
        return obj

def connect_to_db():
    try:
        connection = psycopg2.connect(
            user=sql_user,
            password=sql_password,
            host=sql_host,
            port=sql_port,
            database=sql_database
        )
        cursor = connection.cursor()
        return connection, cursor
    except Exception as error:
        print(f"Error connecting to the database: {error}")
        return None, None

def main(query: str):
    connection, cursor = connect_to_db()
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        result = [dict(zip([desc[0] for desc in cursor.description], record)) for record in records]
        return convert_decimal(result)
    finally:
        cursor.close()
        connection.close()

def get_result(name_or_id: str):
    # query = f"SELECT anchor_nickname, author_id, subsidiary, team, operations FROM daily.wechat_live WHERE data_date BETWEEN '2025-04-01' AND '2025-04-30' AND (anchor_nickname = '{name_or_id}' OR author_id = '{name_or_id}');"
    query = f"""
        SELECT anchor_nickname, author_id, subsidiary, team, operations
        FROM daily.wechat_live
        WHERE (anchor_nickname = '{name_or_id}' OR author_id = '{name_or_id}')
        ORDER BY data_date DESC
        LIMIT 1;
        """
    reply = Reply(ReplyType.TEXT)
    content = main(query)

    if not content:
        reply.content = f"没有找到{name_or_id}的相关数据"
        return reply
    return_text = f"视频号昵称: {content[0]['anchor_nickname']}\n" \
                  f"视频号ID: {content[0]['author_id']}\n" \
                  f"运营: {content[0]['operations']}\n" \
                  f"小组: {content[0]['team']}\n" \
                  f"分公司: {content[0]['subsidiary']}"
    reply.content = return_text
    print(return_text)
    return reply

# if __name__ == "__main__":
#     name_or_id = "sphyn35WHKoAsV7"
#     result = get_result(name_or_id)
