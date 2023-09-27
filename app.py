import sqlite3
import time
import sys
import matplotlib.pyplot as plt
import atexit

# Connect to the database or create it if it doesn't exist
conn = sqlite3.connect('data_collection.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS collected_data (
        id INTEGER PRIMARY KEY,
        category TEXT,
        input_data REAL,
        output_emissions REAL
    )
''')

# Function to insert data into the database
def insert_data(category, input_data, output_emissions):
    cursor.execute('INSERT INTO collected_data (category, input_data, output_emissions) VALUES (?, ?, ?)', (category, input_data, output_emissions))
    conn.commit()



def waste_disposal_emissions():

    age_groups = {
    "Below 18 to 30": 30, 
    "31 to 50": 36, 
    "51 and above": 24
    }


    print("Select your age group:")
    for i, age_group in enumerate(age_groups.keys()):
        print(f"{i + 1}. {age_group}")
    
    selection = int(input("Enter the number corresponding to your age group: "))
    selected_age_group = list(age_groups.keys())[selection - 1]

    generated_waste = input("Did you generate waste? (yes/no): ").lower()

    if generated_waste == 'yes':
        waste_weight = age_groups[selected_age_group]
    else:
        waste_weight = 0

    output_emissions = waste_weight * 0.700  # Here, 0.700 is a generic emission factor you might want to adjust
    print(output_emissions, 'Emissions in KgCO2')
    insert_data('waste_disposal_emissions', waste_weight, output_emissions)
    return output_emissions





def calculate_all_travel_emissions():
    # Dictionary to hold the emission factors for each travel type
    emission_factors = {
        'air': 0.440,
        'train': 0.072,
        'car': 0.240
    }
    
    total_emissions = 0

    # Iterate through all travel types and get user input
    for travel_type, factor in emission_factors.items():
        user_response = input(f"Did you travel by {travel_type} (yes/no): ").strip().lower()
        
        if user_response == 'yes':
            distance = float(input(f"Enter distance travelled by {travel_type} (miles): "))
            emissions = distance * factor
            print(emissions, 'Emissions in KgCO2 for', travel_type)
            total_emissions += emissions
            insert_data(travel_type + '_travel_emissions', distance, emissions)
            
        elif user_response == 'no':
            print(f"No emissions from {travel_type} travel.")
            insert_data(travel_type + '_travel_emissions', 0, 0)
            
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
            return
    
    print("Total emissions: ", total_emissions, 'KgCO2')
    return total_emissions


def energy_emissions():
    usage = input("Did you use electricity or gas? (yes/no): ").lower()
    if usage == 'yes':
        # For electricity
        electricity_bill = float(input("Enter electricity bill (pounds): "))
        electricity_emissions = electricity_bill * 0.685294118
        print(electricity_emissions, 'Electricity emissions in KgCO2')
        insert_data('electricity_consumption_emissions', electricity_bill, electricity_emissions)

        # For gas
        gas_meter_type = input("Select gas meter type (imperial/metric): ").lower()

        if gas_meter_type == 'imperial':
            gas_bill = float(input("Enter gas bill for imperial meter (pounds): "))
            gas_emissions = gas_bill * 6.4434483
            print(gas_emissions, 'Gas emissions in KgCO2 for imperial meter')
            insert_data('gas_imperial_meter_emissions', gas_bill, gas_emissions)

        elif gas_meter_type == 'metric':
            gas_bill = float(input("Enter gas bill for metric meter (pounds): "))
            gas_emissions = gas_bill * 6.4484259
            print(gas_emissions, 'Gas emissions in KgCO2 for metric meter')
            insert_data('gas_metric_meter_emissions', gas_bill, gas_emissions)

        else:
            print("Invalid meter type selected.")
            return
    elif usage == 'no':
        print("No emissions calculated as no energy was used.")
    else:
        print("Invalid selection. Please enter 'yes' or 'no'.")
        return



# Test the function


def calculate_diet_emissions():
    # Dictionary to hold the caloric values for each age and gender category
    caloric_values = {
        '18 and below': {'male': 72000, 'female': 58500},
        '19-30': {'male': 80400, 'female': 62400},
        '31-50': {'male': 77000, 'female': 60000},
        '51 and above': {'male': 70000, 'female': 55000}
    }
    
    conversion_factors = {
        'vegan': 0.00069,
        'vegetarian': 0.00116,
        'omnivorous': 0.00223,
        'pescetarian': 0.00166,
        'paleo': 0.00262,
        'keto': 0.00291
    }
    
    # Prompt the user to select an age category
    print("Select an age category:")
    for i, age in enumerate(caloric_values.keys(), start=1):
        print(f"{i}. {age}")
    
    age_selection = int(input("Enter the number corresponding to your age category: "))
    
    if 1 <= age_selection <= len(caloric_values):
        age_category = list(caloric_values.keys())[age_selection - 1]
    else:
        print("Invalid selection.")
        return
    
    # Prompt the user to select a gender
    print("\nSelect gender:")
    print("1. Male")
    print("2. Female")
    
    gender_selection = int(input("Enter the number corresponding to your gender: "))
    gender = 'male' if gender_selection == 1 else 'female'
    
    # Get the caloric value based on the user's age and gender
    user_input = caloric_values[age_category][gender]
    
    # Prompt the user to select a diet type
    print("\nSelect a diet type:")
    for i, diet in enumerate(conversion_factors.keys(), start=1):
        print(f"{i}. {diet.capitalize()}")
    
    diet_selection = int(input("Enter the number corresponding to your diet type: "))
    
    if 1 <= diet_selection <= len(conversion_factors):
        diet_type = list(conversion_factors.keys())[diet_selection - 1]
        conversion_factor = conversion_factors[diet_type]
    else:
        print("Invalid selection.")
        return
    
    # Calculate and print the emissions
    output_emissions = user_input * conversion_factor
    print(output_emissions, 'Emissions in KgCO2')
    
    # Call to a previously defined insert_data function
    insert_data(diet_type + '_emissions', user_input, output_emissions)
    return output_emissions



def Database():
    cursor.execute('SELECT * FROM collected_data')
    data = cursor.fetchall()
    for row in data:
        print(row)
    return data

def create_pie_chart():
    cursor.execute('SELECT category, COUNT(*) as count FROM collected_data GROUP BY category')
    chart_data = cursor.fetchall()
    labels = [row[0] for row in chart_data]
    sizes = [row[1] for row in chart_data]

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Emissions_Distribution')
    plt.show()

    
def quit():
    print("The tasks are completed.....")
    time.sleep(2)
    sys.exit()

# Your existing menu function...

def menu():
    print("***MAIN MENU***")
    time.sleep(1)

    choice = input("""\

                        a: waste_disposal_emissions()
                        b: calculate_all_travel_emissions() 
                        c: energy_emissions()                       
                        d: calculate_diet_emissions()                           
                        x: database
                        z: create_pie_chart
                        q: quit

                        PLEASE SELECT FROM a, b, c, d, e, f, g, h, x, z, q:


    """)
    if  choice =="a":
        output_emissions = waste_disposal_emissions()
        menu()
    elif choice =="b":
        output_emissions = calculate_all_travel_emissions()
        menu()
    
    elif choice =="c":
        output_emissions = energy_emissions()  
        menu()
    elif choice =="d":
        output_emissions = calculate_diet_emissions()
        menu()
            
    elif choice =="x":
        output = Database()
        menu()
    elif choice =="z":
        output = create_pie_chart()
        menu()
    elif choice =="q":
        quit()
    else:
        print("Error, you must choose a valid option")
        menu()

    print(df)


# Close the connection when the program ends
atexit.register(conn.close)

menu()
