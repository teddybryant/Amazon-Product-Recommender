import sqlite3

# Function to parse the dataset text file
def parse_dataset(file_path):
    products = []
    current_product = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('Id:'):
                if current_product:
                    products.append(current_product)
                    current_product = {}
                current_product['id'] = line.split('Id:')[1].strip()
            elif line.startswith('ASIN:'):
                current_product['ASIN'] = line.split('ASIN:')[1].strip()
            elif line.startswith('title:'):
                current_product['title'] = line.split('title:')[1].strip()
            elif line.startswith('group:'):
                current_product['group'] = line.split('group:')[1].strip()
            elif line.startswith('salesrank:'):
                current_product['salesrank'] = line.split('salesrank:')[1].strip()
            elif line.startswith('similar:'):
                similar_asins = line.split('similar:')[1].strip().split()[1:]
                current_product['similar'] = similar_asins
            elif line.startswith('categories:'):
                categories = []
                while True:
                    line = next(file).strip()
                    if not line.startswith('|'):
                        break
                    categories.append(line.split('|')[-1].strip())
                current_product['categories'] = categories

            if line.startswith('reviews:'):
                current_product['reviews'] = line.split('reviews:')[1].strip()
    if current_product:
        products.append(current_product)
    return products

# Function to create SQLite database and table
def create_sqlite_db(products):
    conn = sqlite3.connect('products2.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id TEXT,
            ASIN TEXT,
            title TEXT,
            group_name TEXT,
            salesrank TEXT,
            similar TEXT,
            categories TEXT,
            reviews TEXT
        )
    ''')

    # Insert data into the table
    for product in products:
        if 'similar' in product and product['similar'] and product['similar'] != ['0']:
            cursor.execute('''
                INSERT INTO Products (id, ASIN, title, group_name, salesrank, similar, categories, reviews)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.get('id', ''),
                product.get('ASIN', ''),
                product.get('title', ''),
                product.get('group', ''),
                product.get('salesrank', ''),
                ','.join(product.get('similar', [])),
                ','.join(product.get('categories', [])),
                product.get('reviews', '')
            ))

    # Commit changes and close connections
    conn.commit()
    cursor.close()
    conn.close()

# Path to your dataset file
file_path = 'amazon-meta.txt'

# Parse the dataset
products_data = parse_dataset(file_path)

# Create SQLite database and insert data
create_sqlite_db(products_data)
