import sqlite3
import random
import time
import math

def open_db(db_name):
    # Function to connect to the SQLite database
    conn = sqlite3.connect(db_name)
    return conn

def calculate_salesrank_score(salesrank,weight):
    if weight == 0:
        return 0
    else:
        increment = int(4000000/(weight*1000))
        points = weight
        for i in range(0,4000000,increment):
            if i <= salesrank <= i + increment:
                return round(points, 3)
            points-=0.0001
        return 0

def calculate_rating_score(rating, weight):
    if weight == 0:
        return 0
    else:
        increment = weight / 9
        points = weight 

        for i in range(10, 1, -1): 
            current_rating = i / 2 
            if current_rating == rating:
                return round(points, 2)
            points -= increment

        return 0

def algorithm(conn, target_asin, weights, k):
    cursor = conn.cursor()

    # Fetch the attributes for the target product by ASIN
    cursor.execute("SELECT group_name, categories FROM Products WHERE ASIN = ?", (target_asin,))
    target_attributes = cursor.fetchone()

    if target_attributes:
        target_group, target_categories = target_attributes
        target_categories = target_categories.split(',')

        # Calculate a score for each product based on weighted attributes
        cursor.execute("SELECT ASIN, group_name, categories, salesrank, reviews FROM Products")
        all_products = cursor.fetchall()

        scores = []
        for product in all_products:
            asin, group, categories, salesrank, reviews = product
            # Weighted comparisons for 'group', 'categories'
            group_score = weights['group'] * int(group == target_group) 
           
            #  Extract last category for comparison
            categories_score = 0
    
            categories = categories.split(',')
            matching_categories = set(target_categories).intersection(categories)
            categories_score = ((1 / (1 + math.exp(-len(matching_categories))))-0.5)*2*weights['categories']

            # Calculate sales rank score using the calculate_salesrank_score function
            if salesrank.isdigit():
                salesrank_score = calculate_salesrank_score(int(salesrank),weights['salesrank'])
            else:
                salesrank_score = 0
            
            # Extract and compare average ratings for 'reviews'
            rating = float(reviews.split('avg rating: ')[1]) if 'avg rating: ' in reviews else 0
            reviews_score  = float(calculate_rating_score(rating,weights['reviews']))
            # Calculate total score for each product
            total_score = group_score + categories_score + salesrank_score + reviews_score
            scores.append((asin, total_score))

        # Sort products by total score and select top 5 recommendations
        scores.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = scores[:k]

        return top_recommendations

    else:
        return None
    
def conduct_test(conn, n, weights, k):
    success_counter = 0
    total_counter = 0
    total_counted = 0
    iteration_count = 0

    for _ in range(n):
        # Generate a random product ID
        cursor = conn.cursor()
        while True:
            random_id = random.randint(1, 548551)
            cursor.execute("SELECT ASIN, similar FROM Products WHERE Id = ?", (random_id,))
            target_attributes = cursor.fetchone()

            if target_attributes:
                ASIN, similar = target_attributes
                similar = similar.split(',')
                break  # Exit the loop when a valid row is found

        # Run your algorithm for the same product
        recommendations = algorithm(conn, ASIN, weights, k)
        if similar:
            for product_asin in similar:
                total_counted+=1
                # Check if the product ASIN is in the database
                cursor.execute("SELECT ASIN FROM Products WHERE ASIN = ?", (product_asin,))
                result = cursor.fetchone()
                if result is not None:
                    total_counter += 1

                    # Check if ASIN is in the recommendation
                    recommended_asins = [item[0] for item in recommendations]
                    if product_asin in recommended_asins:
                        success_counter += 1
        iteration_count+=1
        print("ASIN VALUE: " + str(ASIN))
        print("Similar: " + str(similar))
        print("Recommended: " + str(recommendations))
        print("ITERATION: " + str(iteration_count)+ "\n")
    return success_counter, total_counter, total_counted

import sqlite3

# Open the database
db_name = 'products2.db'  # Replace with your database name/path
connection = open_db(db_name)

# Example weights (adjust as needed)
weights = {
    'group': 1,
    'categories': 5,
    'salesrank': 1,
    'reviews': 1
}

start_time = time.time()
print(conduct_test(connection, 1, weights,5))
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
# Close the database connection
connection.close()
