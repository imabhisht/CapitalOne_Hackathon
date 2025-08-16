# Agriculture Data Loader

Scripts and data files for loading Indian district-level agriculture datasets into MongoDB. The pipeline loads CSVs, adds geolocation coordinates, and enables geospatial queries.

## Contents

- `data_loader.py` — Loads CSV datasets into MongoDB collections
- `add_geolocation.py` — Geocodes district-state pairs and creates geospatial indexes
- `*.csv` — Raw agriculture data files
- `geocode_cache.json` — (Auto-generated) Caches geocoding results

## Prerequisites

- Python 3.11+
- MongoDB (local or remote instance)
- [Google Maps API Key](https://developers.google.com/maps/documentation/geocoding/get-api-key) (optional, for improved geocoding)

## Dependencies

The data loading scripts use these key libraries:
- **PyMongo**: MongoDB driver for data insertion and querying
- **Requests**: HTTP client for geocoding API calls
- **Python-dotenv**: Environment variable management

When run from the backend environment, the scripts benefit from the enhanced logging system with colorlog providing color-coded output and structured formatting for better debugging visibility.

## Setup

1. **Install dependencies:**
	```bash
	pip install pymongo python-dotenv requests
	```
	
	Or if using the backend environment (recommended):
	```bash
	cd ../backend && pip install -e .
	```
	
	The backend installation includes all required dependencies including the enhanced requests library for improved geocoding performance.
2. **Configure environment variables:**
	```bash
	cp .env.example .env
	```
	Edit `.env` with your MongoDB URL and API keys.
3. **Place all CSV files** in this directory.
4. **Ensure MongoDB is running** and accessible at the URL you provided.

## Usage

### 1. Load Data into MongoDB

```bash
python data_loader.py
```
- Loads all CSVs into the `agriculture_data` database.
- Progress and errors are logged to `dataloading.log`.
- When run from the backend environment, benefits from color-coded console logging for real-time progress visibility.

### 2. Add Geolocation Coordinates

```bash
python add_geolocation.py
```
- Geocodes all unique district-state pairs using OpenStreetMap (and Google Maps if API key is set).
- Updates all collections with `latitude`, `longitude`, and a GeoJSON `coordinates` field.
- Creates geospatial indexes for efficient spatial queries.
- Logs progress to `geocoding.log` and caches results in `geocode_cache.json`.
- Enhanced console output with color-coded logging when run from the backend environment.

## File Descriptions

- **data_loader.py**: Reads each CSV, converts types safely, and inserts documents into MongoDB collections. Handles missing/invalid data gracefully.
- **add_geolocation.py**: Finds all unique district-state pairs, geocodes them (with caching and fallback), updates all collections, and creates 2dsphere indexes.
- **.env.example**: Template for required environment variables.
- **geocode_cache.json**: (Generated) Stores geocoding results to avoid redundant API calls.

## Notes

- **API Limits:** The scripts include delays to respect geocoding service rate limits. For large datasets, geocoding may take time.
- **Google Maps API Key:** Optional, but recommended for higher accuracy and fallback if OpenStreetMap fails.
- **Data Integrity:** Only rows with valid district and state are processed for geocoding.

## Customization

- To add new datasets, update both `data_loader.py` and `add_geolocation.py` to include new collections.
- To change geocoding logic, edit the `geocode_location` function in `add_geolocation.py`.
