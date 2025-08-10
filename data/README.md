# Agriculture Data Loader

This directory contains scripts and data files for loading, enriching, and preparing Indian district-level agriculture datasets for analysis. The pipeline loads CSVs into MongoDB, adds geolocation coordinates, and enables geospatial queries.

## Contents

- `data_loader.py` — Loads all CSV datasets into MongoDB collections with type-safe conversion and logging.
- `add_geolocation.py` — Geocodes all unique district-state pairs, updates collections with latitude/longitude, and creates geospatial indexes.
- `crop_production_data.csv`, `irrigation_source_data.csv`, `max_temperature_data.csv`, `min_temperature_data.csv`, `precipitation_data.csv` — Raw data files to be loaded.
- `geocode_cache.json` — (Auto-generated) Caches geocoding results to minimize API calls.
- `.env sample` — Example environment variable file for MongoDB and Google Maps API key.

## Prerequisites

- Python 3.7+
- MongoDB (local or remote instance)
- [Google Maps API Key](https://developers.google.com/maps/documentation/geocoding/get-api-key) (optional, for improved geocoding)

## Setup

1. **Install dependencies:**
	```bash
	pip install pymongo python-dotenv requests
	```
	
	Or if using the backend environment:
	```bash
	cd ../backend && pip install -e .
	```
2. **Configure environment variables:**
	- Copy `.env sample` to `.env` and fill in your MongoDB URL and (optionally) Google Maps API key:
	  ```
	  MONGO_URL=mongodb://localhost:27017/
	  GOOGLE_MAPS_API_KEY=your_google_maps_api_key
	  ```
3. **Place all CSV files** in this directory.
4. **Ensure MongoDB is running** and accessible at the URL you provided.

## Usage

### 1. Load Data into MongoDB

```bash
python data_loader.py
```
- Loads all CSVs into the `agriculture_data` database.
- Progress and errors are logged to `dataloading.log`.

### 2. Add Geolocation Coordinates

```bash
python add_geolocation.py
```
- Geocodes all unique district-state pairs using OpenStreetMap (and Google Maps if API key is set).
- Updates all collections with `latitude`, `longitude`, and a GeoJSON `coordinates` field.
- Creates geospatial indexes for efficient spatial queries.
- Logs progress to `geocoding.log` and caches results in `geocode_cache.json`.

## File Descriptions

- **data_loader.py**: Reads each CSV, converts types safely, and inserts documents into MongoDB collections. Handles missing/invalid data gracefully.
- **add_geolocation.py**: Finds all unique district-state pairs, geocodes them (with caching and fallback), updates all collections, and creates 2dsphere indexes.
- **.env sample**: Template for required environment variables.
- **geocode_cache.json**: (Generated) Stores geocoding results to avoid redundant API calls.

## Notes

- **API Limits:** The scripts include delays to respect geocoding service rate limits. For large datasets, geocoding may take time.
- **Google Maps API Key:** Optional, but recommended for higher accuracy and fallback if OpenStreetMap fails.
- **Data Integrity:** Only rows with valid district and state are processed for geocoding.

## Customization

- To add new datasets, update both `data_loader.py` and `add_geolocation.py` to include new collections.
- To change geocoding logic, edit the `geocode_location` function in `add_geolocation.py`.
