"""
Create comprehensive sample data for tech routing system
35 Customers + 15 Technicians with Melbourne addresses
"""
import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample data with 35 customers and 15 technicians"""
    
    # Melbourne suburb addresses
    suburbs = {
        'Clayton': ['Clayton Road, Clayton VIC 3168', 'Clayton Campus, Monash University, Clayton VIC 3168', 'Central Road, Clayton VIC 3168'],
        'Dandenong': ['Dandenong Railway Station, Dandenong VIC 3175', 'Princes Highway, Dandenong VIC 3175', 'Robinson Street, Dandenong VIC 3175'],
        'Mulgrave': ['Mulgrave Business Park, Mulgrave VIC 3170', 'Ferntree Gully Road, Mulgrave VIC 3170', 'Springvale Road, Mulgrave VIC 3170'],
        'Tarneit': ['Derrimut Road, Tarneit VIC 3029', 'Tarneit Road, Tarneit VIC 3029', 'Dohertys Road, Tarneit VIC 3029'],
        'CBD': ['Collins Street, Melbourne VIC 3000', 'Bourke Street, Melbourne VIC 3000', 'Swanston Street, Melbourne VIC 3000', 
                'Flinders Street, Melbourne VIC 3000', 'Elizabeth Street, Melbourne VIC 3000', 'Exhibition Street, Melbourne VIC 3000'],
        'Richmond': ['Bridge Road, Richmond VIC 3121', 'Swan Street, Richmond VIC 3121'],
        'Carlton': ['Lygon Street, Carlton VIC 3053', 'Rathdowne Street, Carlton VIC 3053'],
        'South Yarra': ['Chapel Street, South Yarra VIC 3141', 'Commercial Road, South Yarra VIC 3141'],
        'St Kilda': ['Fitzroy Street, St Kilda VIC 3182', 'Acland Street, St Kilda VIC 3182'],
        'Footscray': ['Barkly Street, Footscray VIC 3011', 'Nicholson Street, Footscray VIC 3011']
    }
    
    # Service types
    service_types = [
        'Gas Leak Repair',
        'Electrical Fault',
        'Plumbing Issue',
        'HVAC Maintenance',
        'Appliance Installation',
        'Emergency Callout',
        'Routine Service',
        'Maintenance Check',
        'Safety Inspection',
        'System Upgrade'
    ]
    
    # Skills
    skills = ['Plumbing', 'Electric', 'HVAC', 'IT', 'Roofing', 'Gas', 'Solar', 'Carpentry', 'Cleaning', 'Security']
    
    # Customer skill mapping (each customer needs one specific skill)
    customer_skill_map = {
        'Gas Leak Repair': 'Gas',
        'Electrical Fault': 'Electric',
        'Plumbing Issue': 'Plumbing',
        'HVAC Maintenance': 'HVAC',
        'Appliance Installation': 'Electric',
        'Emergency Callout': 'Plumbing',
        'Routine Service': 'Plumbing',
        'Maintenance Check': 'Electric',
        'Safety Inspection': 'Security',
        'System Upgrade': 'IT'
    }
    
    # Generate customers
    customers = []
    names = [
        ('John', 'Smith'), ('Mary', 'Johnson'), ('David', 'Williams'), ('Sarah', 'Brown'),
        ('Michael', 'Jones'), ('Emma', 'Garcia'), ('James', 'Miller'), ('Olivia', 'Davis'),
        ('Robert', 'Rodriguez'), ('Sophia', 'Martinez'), ('William', 'Hernandez'), ('Isabella', 'Lopez'),
        ('Richard', 'Gonzalez'), ('Mia', 'Wilson'), ('Joseph', 'Anderson'), ('Charlotte', 'Thomas'),
        ('Thomas', 'Taylor'), ('Amelia', 'Moore'), ('Charles', 'Jackson'), ('Harper', 'Martin'),
        ('Christopher', 'Lee'), ('Evelyn', 'Thompson'), ('Daniel', 'White'), ('Abigail', 'Harris'),
        ('Matthew', 'Sanchez'), ('Emily', 'Clark'), ('Anthony', 'Ramirez'), ('Elizabeth', 'Lewis'),
        ('Mark', 'Robinson'), ('Sofia', 'Walker'), ('Donald', 'Young'), ('Avery', 'Allen'),
        ('Steven', 'King'), ('Victoria', 'Wright'), ('Paul', 'Scott')
    ]
    
    # 35 Customers
    for i in range(35):
        first_name, last_name = names[i]
        suburb = random.choice(list(suburbs.keys()))
        address = f"{random.randint(1, 999)} {random.choice(suburbs[suburb])}"
        service_type = random.choice(service_types)
        required_skill = customer_skill_map.get(service_type, 'Plumbing')
        
        # Tight time window: maximum 2 hours (all on November 1st)
        # Daytime only: between 8 AM and 6 PM
        window_start_hour = random.randint(8, 16)  # Start between 8 AM and 4 PM
        window_duration_hours = random.randint(1, 2)  # Window is 1-2 hours max
        window_end_hour = window_start_hour + window_duration_hours
        
        # Ensure window doesn't go past 6 PM
        if window_end_hour > 18:
            window_end_hour = 18
            window_start_hour = window_end_hour - window_duration_hours
            if window_start_hour < 8:
                window_start_hour = 8
        
        # All dates set to November 1st, 2025
        date = '2025-11-01'
        
        customer = {
            'Type': 'Customer',
            'Username': f"{first_name.lower()}_{last_name.lower()}",
            'Email': f"{first_name.lower()}.{last_name.lower()}@example.com",
            'Password': 'Welcome123',
            'Phone': f"04{random.randint(10000000, 99999999)}",
            'Address': address,
            'ServiceMinutes': random.choice([60, 90, 120, 180]),
            'WindowStart': f"{date} {window_start_hour:02d}:00",
            'WindowEnd': f"{date} {window_end_hour:02d}:00",
            'RequiredSkills': required_skill,
            'Priority': random.choice(['High', 'Medium', 'Low']),
            'ServiceType': service_type,
            'DepotAddress': '',
            'CapacityHours': '',
            'ShiftStart': '',
            'ShiftEnd': '',
            'Skills': '',
            'ColorHex': ''
        }
        customers.append(customer)
    
    # Generate technicians (15 techs with multiple skills)
    tech_names = [
        ('Alex', 'Taylor'), ('Jordan', 'Martinez'), ('Casey', 'Anderson'),
        ('Drew', 'Thompson'), ('Blake', 'Robinson'), ('Quinn', 'Walker'),
        ('Riley', 'Young'), ('Cameron', 'King'), ('Taylor', 'Wright'),
        ('Morgan', 'Scott'), ('Jamie', 'Green'), ('Sage', 'Adams'),
        ('Avery', 'Nelson'), ('Dakota', 'Baker'), ('Reese', 'Hill')
    ]
    
    # Technician skill combinations (each tech has 2-4 skills)
    tech_skill_combos = [
        ['Plumbing', 'Gas'],
        ['Electric', 'Solar'],
        ['HVAC', 'Electric'],
        ['IT', 'Electric'],
        ['Plumbing', 'Cleaning'],
        ['Roofing', 'Carpentry'],
        ['Electric', 'HVAC', 'IT'],
        ['Plumbing', 'Gas', 'Carpentry'],
        ['Solar', 'Electric', 'HVAC'],
        ['Gas', 'HVAC', 'Plumbing'],
        ['Electric', 'Plumbing', 'Security'],
        ['IT', 'Security'],
        ['Roofing', 'Carpentry', 'Cleaning'],
        ['HVAC', 'Plumbing'],
        ['Electric', 'Solar', 'HVAC', 'IT']
    ]
    
    technicians = []
    for i in range(15):
        first_name, last_name = tech_names[i]
        suburb = random.choice(list(suburbs.keys()))
        depot_address = f"{random.randint(1, 999)} {random.choice(suburbs[suburb])}"
        
        # Technician shifts: 4-8 hours, different start times during the day (not night)
        # Start times: between 6 AM and 2 PM (daytime only)
        shift_start_hour = random.randint(6, 14)  # Start between 6 AM and 2 PM
        shift_duration_hours = random.choice([4, 5, 6, 7, 8])  # Shift is 4-8 hours
        shift_end_hour = shift_start_hour + shift_duration_hours
        
        # Ensure shift doesn't go past 6 PM (daytime only, not night)
        if shift_end_hour > 18:
            shift_end_hour = 18
            shift_duration_hours = shift_end_hour - shift_start_hour
            if shift_duration_hours < 4:
                # Adjust start time if needed
                shift_start_hour = shift_end_hour - 4
        
        shift_start = f"{shift_start_hour:02d}:00"
        shift_end = f"{shift_end_hour:02d}:00"
        
        tech = {
            'Type': 'Technician',
            'Username': f"tech_{first_name.lower()}",
            'Email': f"tech.{first_name.lower()}@company.com",
            'Password': 'Welcome123',
            'Phone': f"04{random.randint(10000000, 99999999)}",
            'Address': '',
            'ServiceMinutes': '',
            'WindowStart': '',
            'WindowEnd': '',
            'RequiredSkills': '',
            'Priority': '',
            'ServiceType': '',
            'DepotAddress': depot_address,
            'CapacityHours': shift_duration_hours,
            'ShiftStart': shift_start,
            'ShiftEnd': shift_end,
            'Skills': ', '.join(tech_skill_combos[i]),
            'ColorHex': random.choice(['#4285F4', '#34A853', '#FBBC05', '#EA4335', '#FF6D01'])
        }
        technicians.append(tech)
    
    # Combine all data
    all_data = customers + technicians
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Shuffle rows
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save to Excel
    output_file = 'sample_data_50_people.xlsx'
    df.to_excel(output_file, index=False, sheet_name='Bulk Upload')
    
    print(f"✓ Created {output_file}")
    print(f"✓ Total records: {len(df)}")
    print(f"✓ Customers: {len(customers)}")
    print(f"✓ Technicians: {len(technicians)}")
    print(f"✓ Skills covered: {', '.join(skills)}")
    print(f"✓ Service types: {len(service_types)}")
    print(f"\nLocation: {output_file}")
    
    return df

if __name__ == '__main__':
    df = create_sample_data()
    print("\nSample preview:")
    print(df[['Type', 'Username', 'Email', 'Address', 'DepotAddress']].head(10))

