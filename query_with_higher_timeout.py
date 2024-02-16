import psycopg2
import json

# Load configurations from config.json
with open('config.json', 'r') as file:
    config = json.load(file)

# Use the configurations in the script
host = config['POSTGRE']['HOST']
database = config['POSTGRE']['DATABASE']
user = config['POSTGRE']['USER']
password = config['POSTGRE']['PASSWORD']

# Establish the connection
print("Connecting to the database...")
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
print("Connected successfully!")

# Set the connection to autocommit mode
conn.autocommit = True

# Create a cursor object to interact with the database
cur = conn.cursor()


def main():
    # Set the statement timeout for the session to 10 seconds
    cur.execute("SET statement_timeout = 1000000;")
    print("Statement timeout set to 1000 seconds.")

    print("Executing SQL query...")
    # sql_query = 'VACUUM ANALYZE "Embeddings";'
    # sql_query = 'CREATE INDEX Embeddings_embedding ON "Embeddings" USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);'
    # sql_query = 'CREATE INDEX embeddings_cosine_idx ON "Embeddings" USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);'
    sql_query = 'Type your query here'
    cur.execute(sql_query)
    print("SQL query executed successfully!")


if __name__ == "__main__":
    main()
