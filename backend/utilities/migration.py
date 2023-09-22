import psycopg2
import os

def truncate_table(conn, table_name):
    print(f"Truncating table {table_name}...")
    cur = conn.cursor()
    cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY;")
    conn.commit()
    cur.close()
    print(f"Successfully truncated table {table_name}.")

def export_data(conn, table_name, file_name):
    print(f"Exporting data from table {table_name} to file {file_name}...")
    cur = conn.cursor()
    with open(file_name, 'w') as f:
        cur.copy_expert(f"COPY {table_name} TO STDOUT WITH CSV HEADER", f)
    cur.close()
    print(f"Successfully exported data from table {table_name} to file {file_name}.")

def import_data(conn, table_name, file_name):
    print(f"Importing data into table {table_name} from file {file_name}...")
    cur = conn.cursor()
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r') as f:
        # Count the number of rows in the CSV (excluding header)
        row_count = sum(1 for row in f) - 1
        print(f"CSV contains {row_count} data rows.")

        # Rewind the file pointer to the beginning of the file
        f.seek(0)

        # Perform the import
        cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)

    conn.commit()
    cur.close()
    print(f"Successfully imported data into table {table_name} from file {file_name}.")

def get_table_names(conn):
    print("Getting table names...")
    cur = conn.cursor()
    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
    tables = [table[0] for table in cur.fetchall()]
    cur.close()
    print("Successfully retrieved table names.")
    return tables

def clone_schema(old_conn, new_conn, table_name):
    print(f"Cloning schema for table {table_name}...")
    old_cur = old_conn.cursor()
    new_cur = new_conn.cursor()

    new_cur.execute(f"SELECT to_regclass('{table_name}');")
    table_exists = new_cur.fetchone()[0]

    if table_exists is None:
        old_cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
        schema = old_cur.fetchall()

        columns = ', '.join([f"{col[0]} {col[1]}" for col in schema])
        new_cur.execute(f"CREATE TABLE {table_name} ({columns});")
        new_conn.commit()
        print(f"Successfully cloned schema for table {table_name}.")

    old_cur.close()
    new_cur.close()

if __name__ == '__main__':
    print("Connecting to the old and new PostgreSQL databases...")
    old_conn = psycopg2.connect(
        host="ep-crimson-rain-043243.us-west-2.retooldb.com",
        database="retool",
        user="retool",
        password="QXR1HE3hgVxf",
        port="5432"
    )
    new_conn = psycopg2.connect(
        host="burnmypoints-prod.c0ctr64rgeg6.us-east-2.rds.amazonaws.com",
        database="burnmypoints_prod",
        user="wirrie",
        password="Williezhou13!",
        port="5432"
    )
    print("Successfully connected.")

    table_names = get_table_names(old_conn)

    for table_name in table_names:
        print(f"Starting migration for table {table_name}...")
        file_name = f"{table_name}.csv"

        clone_schema(old_conn, new_conn, table_name)
        truncate_table(new_conn, table_name)
        # export_data(old_conn, table_name, file_name)
        import_data(new_conn, table_name, file_name)
        print(f"Completed migration for table {table_name}.")

    print("Closing database connections...")
    old_conn.close()
    new_conn.close()
    print("Connections closed. Migration completed.")