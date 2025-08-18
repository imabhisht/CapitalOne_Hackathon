import pymongo
import os
import dotenv
import csv
import logging

logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler('dataloading.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logging.getLogger().addHandler(handler)

dotenv.load_dotenv()

connection = pymongo.MongoClient(os.getenv("MONGO_URL"))

# CSV file paths
district_wise_crop_production_data = 'crop_production_data.csv'
district_wise_irrigation_source_data = 'irrigation_source_data.csv'
district_wise_max_temperature_data = 'max_temperature_data.csv'
district_wise_min_temperature_data = 'min_temperature_data.csv'
district_wise_precipitation_data = 'precipitation_data.csv'

database = connection['agriculture_data']

def safe_float_convert(value):
    """Convert string to float, return None if conversion fails"""
    try:
        return float(value) if value and value.strip() else None
    except (ValueError, TypeError):
        return None

def safe_int_convert(value):
    """Convert string to int, return None if conversion fails"""
    try:
        return int(value) if value and value.strip() else None
    except (ValueError, TypeError):
        return None

logging.info("Loading data into MongoDB...")

# Load crop production data
logging.info("Starting with crop production data...")
try:
    with open(district_wise_crop_production_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header
        
        collection = database['crop_production_data']
        documents = []
        
        for row in reader:
            if len(row) >= 12:  # Ensure row has enough columns
                doc = {
                    'year': safe_int_convert(row[1]),
                    'state': row[3].strip() if row[3] else None,
                    'district': row[4].strip() if row[4] else None,
                    'rice': safe_float_convert(row[5]),
                    'wheat': safe_float_convert(row[6]),
                    'sorghum': safe_float_convert(row[7]),
                    'pearl_millet': safe_float_convert(row[8]),
                    'maize': safe_float_convert(row[9]),
                    'fingermillet': safe_float_convert(row[10]),
                    'total_area': safe_float_convert(row[11])
                }
                documents.append(doc)
        
        if documents:
            collection.insert_many(documents)
            logging.info(f"Crop production data loaded successfully. {len(documents)} records inserted.")
        else:
            logging.warning("No valid crop production data found to insert.")
            
except FileNotFoundError:
    logging.error(f"File {district_wise_crop_production_data} not found.")
except Exception as e:
    logging.error(f"Error loading crop production data: {e}", exc_info=True)

# Load irrigation source data
logging.info("Starting with irrigation source data...")
try:
    with open(district_wise_irrigation_source_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header
        
        collection = database['irrigation_source_data']
        documents = []
        
        for row in reader:
            if len(row) >= 11:  # Ensure row has enough columns
                doc = {
                    'year': safe_int_convert(row[1]),
                    'state': row[3].strip() if row[3] else None,  # Added missing state field
                    'district': row[4].strip() if row[4] else None,
                    'canals_area': safe_float_convert(row[5]),
                    'tanks_area': safe_float_convert(row[6]),
                    'tube_wells_area': safe_float_convert(row[7]),
                    'other_wells_area': safe_float_convert(row[8]),
                    'total_well_area': safe_float_convert(row[9]),
                    'other_sources_area': safe_float_convert(row[10])
                }
                documents.append(doc)
        
        if documents:
            collection.insert_many(documents)
            logging.info(f"Irrigation source data loaded successfully. {len(documents)} records inserted.")
        else:
            logging.warning("No valid irrigation source data found to insert.")
            
except FileNotFoundError:
    logging.error(f"File {district_wise_irrigation_source_data} not found.")
except Exception as e:
    logging.error(f"Error loading irrigation source data: {e}", exc_info=True)

# Load max temperature data
logging.info("Starting with max temperature data...")
try:
    with open(district_wise_max_temperature_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header
        
        collection = database['max_temperature_data']
        documents = []
        
        for row in reader:
            if len(row) >= 17:  # Ensure row has enough columns
                doc = {
                    'year': safe_int_convert(row[1]),
                    'state': row[3].strip() if row[3] else None,
                    'district': row[4].strip() if row[4] else None,
                    'january': safe_float_convert(row[5]),
                    'february': safe_float_convert(row[6]),
                    'march': safe_float_convert(row[7]),
                    'april': safe_float_convert(row[8]),
                    'may': safe_float_convert(row[9]),
                    'june': safe_float_convert(row[10]),
                    'july': safe_float_convert(row[11]),
                    'august': safe_float_convert(row[12]),
                    'september': safe_float_convert(row[13]),
                    'october': safe_float_convert(row[14]),
                    'november': safe_float_convert(row[15]),
                    'december': safe_float_convert(row[16])
                }
                documents.append(doc)
        
        if documents:
            collection.insert_many(documents)
            logging.info(f"Max temperature data loaded successfully. {len(documents)} records inserted.")
        else:
            logging.warning("No valid max temperature data found to insert.")
            
except FileNotFoundError:
    logging.error(f"File {district_wise_max_temperature_data} not found.")
except Exception as e:
    logging.error(f"Error loading max temperature data: {e}", exc_info=True)

# Load min temperature data
logging.info("Starting with min temperature data...")
try:
    with open(district_wise_min_temperature_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header
        
        collection = database['min_temperature_data']
        documents = []
        
        for row in reader:
            if len(row) >= 17:  # Ensure row has enough columns
                doc = {
                    'year': safe_int_convert(row[1]),
                    'state': row[3].strip() if row[3] else None,
                    'district': row[4].strip() if row[4] else None,
                    'january': safe_float_convert(row[5]),
                    'february': safe_float_convert(row[6]),
                    'march': safe_float_convert(row[7]),
                    'april': safe_float_convert(row[8]),
                    'may': safe_float_convert(row[9]),
                    'june': safe_float_convert(row[10]),
                    'july': safe_float_convert(row[11]),
                    'august': safe_float_convert(row[12]),
                    'september': safe_float_convert(row[13]),
                    'october': safe_float_convert(row[14]),
                    'november': safe_float_convert(row[15]),
                    'december': safe_float_convert(row[16])
                }
                documents.append(doc)
        
        if documents:
            collection.insert_many(documents)
            logging.info(f"Min temperature data loaded successfully. {len(documents)} records inserted.")
        else:
            logging.warning("No valid min temperature data found to insert.")
            
except FileNotFoundError:
    logging.error(f"File {district_wise_min_temperature_data} not found.")
except Exception as e:
    logging.error(f"Error loading min temperature data: {e}", exc_info=True)

# Load precipitation data
logging.info("Starting with precipitation data...")
try:
    with open(district_wise_precipitation_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip the header
        
        collection = database['precipitation_data']
        documents = []
        
        for row in reader:
            if len(row) >= 17:  # Ensure row has enough columns
                doc = {
                    'year': safe_int_convert(row[1]),
                    'state': row[3].strip() if row[3] else None,  # Added missing state field
                    'district': row[4].strip() if row[4] else None,
                    'january': safe_float_convert(row[5]),
                    'february': safe_float_convert(row[6]),
                    'march': safe_float_convert(row[7]),
                    'april': safe_float_convert(row[8]),
                    'may': safe_float_convert(row[9]),
                    'june': safe_float_convert(row[10]),
                    'july': safe_float_convert(row[11]),
                    'august': safe_float_convert(row[12]),
                    'september': safe_float_convert(row[13]),
                    'october': safe_float_convert(row[14]),
                    'november': safe_float_convert(row[15]),
                    'december': safe_float_convert(row[16])
                }
                documents.append(doc)
        
        if documents:
            collection.insert_many(documents)
            logging.info(f"Precipitation data loaded successfully. {len(documents)} records inserted.")
        else:
            logging.warning("No valid precipitation data found to insert.")
            
except FileNotFoundError:
    logging.error(f"File {district_wise_precipitation_data} not found.")
except Exception as e:
    logging.error(f"Error loading precipitation data: {e}", exc_info=True)

logging.info("Data loading process completed.")

# Close the connection
connection.close()
logging.info("MongoDB connection closed.")