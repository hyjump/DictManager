import sqlite3
import argparse
import os
import sys
import chardet

os.system("color")

def db_connect():
    return sqlite3.connect('DICT.db')

def create_table(conn, Ty):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (Ty,))
    if cursor.fetchone() is None:
        cursor.execute('''CREATE TABLE {} (ID INTEGER PRIMARY KEY AUTOINCREMENT, VALUE TEXT NOT NULL);'''.format(Ty))
        conn.commit()
        print("\033[0;32;40m   {} type data created successfully\033[0m".format(Ty))
    else:
        print("\033[0;32;40m   {} type data already exists\033[0m".format(Ty))

def delete_duplicate(conn, Ty):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM {} WHERE ROWID NOT IN (SELECT MAX(ROWID) FROM {} GROUP BY VALUE)".format(Ty, Ty))
    conn.commit()

def add_value(conn, file_name, Ty, encoding='utf-8'):
    cursor = conn.cursor()
    create_table(conn, Ty)
    file_data = read_file(file_name, encoding)
    dict_values = file_data.splitlines()
    cursor.executemany("INSERT INTO {} (VALUE) VALUES (?)".format(Ty), [(value.strip(),) for value in dict_values if value.strip()])
    conn.commit()
    delete_duplicate(conn, Ty)
    print("\033[0;32;40m   {} type data written successfully\033[0m".format(Ty))

def read_file(file_name, encoding=None):
    with open(file_name, 'rb') as f:
        raw_data = f.read()
    if encoding is None:
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        if encoding is None or result['confidence'] < 0.5:
            raise ValueError("Unable to detect file encoding with high confidence. Please ensure the file is properly encoded and try again.")
    try:
        return raw_data.decode(encoding)
    except UnicodeDecodeError:
        raise ValueError("Failed to decode file with the detected or specified encoding. Please check the file encoding.")

def write_value(conn, filename, Ty_list, encoding='utf-8'):
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS Temp")
        cursor.execute("CREATE TEMPORARY TABLE Temp (VALUE TEXT NOT NULL UNIQUE)")
        for Ty in Ty_list:
            cursor.execute("INSERT OR IGNORE INTO Temp (VALUE) SELECT DISTINCT VALUE FROM {}".format(Ty))
        conn.commit()
        with open(filename, "w", encoding=encoding) as f:
            cursor.execute("SELECT VALUE FROM Temp")
            for row in cursor.fetchall():
                f.write(row[0] + "\n")
        cursor.execute("DROP TABLE IF EXISTS Temp")
        conn.commit()
        print("\033[32m   Database dictionary exported successfully with encoding {}\033[0m".format(encoding))
    except Exception as e:
        print("\033[31m   Error: {}\033[0m".format(e))

def delete_dict_type(conn, Ty_list):
    cursor = conn.cursor()
    for Ty in Ty_list:
        try:
            cursor.execute("DROP TABLE IF EXISTS {}".format(Ty))
            print("\033[0;32;40m   The dictionary type '{}' has been deleted successfully\033[0m".format(Ty))
        except sqlite3.Error as e:
            print("\033[31m   Error occurred while deleting '{}': {}\033[0m".format(Ty, e))
    conn.commit()

def preview_dict_type(dict_type, page_size=50, page=1):
    conn = sqlite3.connect('DICT.db')
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM '{}'".format(dict_type))
    total_rows = cursor.fetchone()[0]
    total_pages = (total_rows + page_size - 1) // page_size
    offset = (page - 1) * page_size
    limit = page_size
    cursor.execute("SELECT VALUE FROM '{}' LIMIT ? OFFSET ?".format(dict_type), (limit, offset))
    values = cursor.fetchall()
    conn.close()
    
    if not values:
        print("\033[31m   No data available for the specified type or page.\033[0m")
        return
    
    print("\n\033[32m   Previewing '{}' type data - Page {} of {}\033[0m".format(dict_type, page, total_pages))
    for value in values:
        print(value[0])
    
    input("\033[31m   Press Enter to load the next 50 rows or Ctrl+C to quit...\033[0m")
    if page < total_pages:
        preview_dict_type(dict_type, page_size, page + 1)

def show_all(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    table_list = cursor.fetchall()
    if not table_list:
        print("\033[31m   Your database dictionary is empty\033[0m")
    else:
        for i in table_list:
            cursor.execute("SELECT count(*) FROM '{}'".format(i[0]))
            count = cursor.fetchone()[0]
            print("\033[32m   Dictionary type: {0:<15} Rows: {1}\033[0m".format(i[0], count))

def main():
    parser = argparse.ArgumentParser(description='A database dictionary')
    parser.add_argument('-i', help='input a dictionary file')
    parser.add_argument('-o', help='output a dictionary file')
    parser.add_argument('-s', help='Show existing dictionary types', action="store_true")
    parser.add_argument('-t', help='Select a type to store in the database || Select one or more dictionary types to export', nargs="*")
    parser.add_argument('-d', help='Delete dictionary types', nargs="*")  
    parser.add_argument('-e', help='Encoding for input/output file', default='utf-8')
    parser.add_argument('-p', help='Preview a dictionary type', nargs="?")
    args = parser.parse_args()

    conn = db_connect()
    try:
        if args.i and args.t:
            add_value(conn, args.i, args.t[0], args.e)
        elif args.o and args.t:
            write_value(conn, args.o, args.t, args.e)
        elif args.s:
            show_all(conn)
        elif args.d:  
            delete_dict_type(conn, args.d)
        elif args.p:
            preview_dict_type(args.p, 50, 1) 
    except Exception as e:
        print("\033[31m   Error: {}\033[0m".format(e))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
