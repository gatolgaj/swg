import sqlite3

# Connect to SQLite database (or create it if it does not exist)
conn = sqlite3.connect('side_effects.db')
cursor = conn.cursor()

# Create a table
cursor.execute('''
CREATE TABLE IF NOT EXISTS side_effects (
    drug_name TEXT,
    side_effect TEXT
)
''')

# Function to insert data into the table
def insert_data(drug_name, side_effect):
    cursor.execute("INSERT INTO side_effects (drug_name, side_effect) VALUES (?, ?)", (drug_name, side_effect))
    conn.commit()

# Read the file and store the data in the database
with open('sample_data.txt', 'r') as file:
    next(file)  # Skip header line
    next(file)  # Skip dashed line under headers
    for line in file:
        if line.strip():  # Skip empty lines
            parts = line.split('\t')  # Split the line on tab to separate fields
            drug_name = parts[0].strip()
            side_effect = parts[1].strip()
            insert_data(drug_name, side_effect)

# Close the database connection
conn.close()

print("Data has been inserted into the database.")
