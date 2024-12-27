import sqlite3
import argparse
import os
import sys
import chardet

# 设置控制台颜色
os.system("color")

def create_table(Ty):     
    conn = sqlite3.connect('DICT.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (Ty,))
    if cursor.fetchone() is None:
        create_table_sql = '''CREATE TABLE %s
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    VALUE TEXT NOT NULL);''' % (Ty)
        cursor.execute(create_table_sql)
        conn.commit()
        print("\033[0;32;40m   %s type data created successfully\033[0m" % (Ty))
    else:
        print("\033[0;32;40m   %s type data already exists\033[0m" % (Ty))
    conn.close()

def delete_duplicate(Ty):   
    conn = sqlite3.connect('DICT.db')
    cursor = conn.cursor()
    delete_duplicate_sql = "DELETE FROM " + Ty + " WHERE ID NOT IN (SELECT MAX(rowid) FROM " + Ty + " GROUP BY VALUE)"
    cursor.execute(delete_duplicate_sql)
    conn.commit()
    conn.close()
    print("\033[0;32;40m   %s type data de-duplication succeeded\033[0m" % (Ty))

def add_value(file_name, Ty, encoding='utf-8'):   
    conn = sqlite3.connect('DICT.db')
    cursor = conn.cursor()
    try:
        create_table(Ty)  # Ensure the table exists
        file_data = read_file(file_name, encoding)
        dict_values = file_data.splitlines()
        for value in dict_values:
            value = value.strip()
            if value:  # Ensure not to insert empty values
                add_sql = "INSERT INTO " + Ty + " (VALUE) VALUES (?)"
                cursor.execute(add_sql, (value,))
        conn.commit()
        delete_duplicate(Ty)
        print("\033[0;32;40m   %s type data written successfully\033[0m" % (Ty))
    except Exception as e:
        print("\033[31m   %s\033[0m" % (e))
    finally:
        conn.close()

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

def write_value(filename, Ty_list, encoding='utf-8'):
    conn = sqlite3.connect('DICT.db')
    cursor = conn.cursor()
    with open(filename, "w", encoding=encoding) as f:
        for Ty in Ty_list:
            take_sql = "SELECT VALUE FROM '{}'".format(Ty)
            cursor.execute(take_sql)
            for row in cursor.fetchall():
                f.write(row[0] + "\n")
    conn.commit()
    conn.close()
    print("\033[32m   Database dictionary exported successfully with encoding {}\033[0m".format(encoding))

def delete_dict_type(Ty_list):
    conn = sqlite3.connect('DICT.db')
    cursor = conn.cursor()
    for Ty in Ty_list:
        try:
            drop_table_sql = "DROP TABLE IF EXISTS {}".format(Ty)
            cursor.execute(drop_table_sql)
            print("\033[0;32;40m   The dictionary type '{}' has been deleted successfully\033[0m".format(Ty))
        except sqlite3.Error as e:
            print("\033[31m   Error occurred while deleting '{}': {}\033[0m".format(Ty, e))
    conn.commit()
    conn.close()

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

def show_all():    
    conn = sqlite3.connect('DICT.db')
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
    conn.commit()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='A database dictionary')
    parser.add_argument('-i', help='input a dictionary file')
    parser.add_argument('-o', help='output a dictionary file')
    parser.add_argument('-s', help='Show existing dictionary types', action="store_true")
    parser.add_argument('-t', help='Select a type to store in the database || Select one or more dictionary types to export', nargs="*")
    parser.add_argument('-d', help='Delete dictionary types', nargs="*")  # 修改这里
    parser.add_argument('-e', help='Encoding for input/output file', default='utf-8')
    parser.add_argument('-p', help='Preview a dictionary type', nargs="?")
    args = parser.parse_args()
    
    if args.i and args.t:
        add_value(args.i, args.t[0], args.e)
    elif args.o and args.t:
        write_value(args.o, args.t, args.e)
    elif args.s:
        show_all()
    elif args.d:  
        delete_dict_type(args.d)
    elif args.p:
        preview_dict_type(args.p, 50, 1)

if __name__ == "__main__":
    main()