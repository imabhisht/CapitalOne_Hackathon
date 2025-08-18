# Soil Water Content Tool Documentation

## Overview

The Soil Water Content (SWC) tool provides access to Planet's satellite-based soil water content data through their Subscriptions API. This tool enables users to access near-daily global soil water content measurements for agricultural monitoring, drought assessment, water resource management, and environmental analysis.

## Features

### Available Functions

1. **`tool_get_soil_water_content`** - Get soil water content data for a specific location
2. **`tool_create_swc_subscription`** - Create a subscription for continuous data delivery
3. **`tool_get_swc_statistics`** - Get statistical analysis of soil water content over time
4. **`tool_get_swc_product_info`** - Get information about available SWC products
5. **`tool_analyze_soil_conditions`** - Analyze soil conditions for agricultural decision making

### Data Products

Planet offers soil water content data at multiple resolutions from two satellite sensors:

#### Spatial Resolutions
- **20m**: High resolution for field-level analysis
- **100m**: Balanced resolution for regional monitoring  
- **1000m**: Lower resolution for large-scale analysis

#### Sensors
- **SMAP**: Soil Moisture Active Passive mission
- **AMSR2**: Advanced Microwave Scanning Radiometer 2

#### Available Product IDs
```
20m Resolution:
  SMAP: SWC-SMAP-L_V1.0_20
  AMSR2: SWC-AMSR2-X_V5.0_20

100m Resolution:
  SMAP: SWC-SMAP-L_V1.0_100
  AMSR2: SWC-AMSR2-X_V5.0_100

1000m Resolution:
  SMAP: SWC-SMAP-L_V1.0_1000
  AMSR2: SWC-AMSR2-X_V5.0_1000
```

## Usage Examples

### 1. Get Soil Water Content Information

```python
from app.modules.tools import tool_get_soil_water_content

# Get soil water content data for a location in Iowa, USA
result = tool_get_soil_water_content(
    lat=41.5868,
    lon=-93.6250,
    resolution="100m",
    sensor="smap",
    days_back=30
)

print(f"Product ID: {result['product_info']['id']}")
print(f"Status: {result['status']}")
print(f"Use Cases: {result['use_cases']}")
```

### 2. Create a Subscription

```python
from app.modules.tools import tool_create_swc_subscription

# Create a subscription for continuous data delivery
subscription = tool_create_swc_subscription(
    lat=41.5868,
    lon=-93.6250,
    resolution="100m",
    sensor="smap",
    cloud_provider="gcs",
    bucket_name="my-swc-data-bucket",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(f"Subscription Status: {subscription['status']}")
```

### 3. Get Product Information

```python
from app.modules.tools import tool_get_swc_product_info

# Get comprehensive product information
info = tool_get_swc_product_info()

print(f"Service: {info['service_overview']['name']}")
print(f"Available Resolutions: {list(info['available_products'].keys())}")

# Show application areas
for area, applications in info['key_applications'].items():
    print(f"{area.title()}: {len(applications)} use cases")
```

### 4. Analyze Soil Conditions for Agriculture

```python
from app.modules.tools import tool_analyze_soil_conditions

# Analyze soil conditions for corn farming
analysis = tool_analyze_soil_conditions(
    lat=41.5868,
    lon=-93.6250,
    crop_type="corn",
    season="summer",
    resolution="100m"
)

print(f"Crop Type: {analysis['analysis_parameters']['crop_type']}")
print(f"Season: {analysis['analysis_parameters']['season']}")
print("Agricultural Recommendations:")
for key in analysis['agricultural_recommendations'].keys():
    print(f"  - {key.replace('_', ' ').title()}")
```

### 5. Get Statistical Analysis

```python
from app.modules.tools import tool_get_swc_statistics

# Get 90-day statistical analysis
stats = tool_get_swc_statistics(
    lat=41.5868,
    lon=-93.6250,
    resolution="100m",
    sensor="smap",
    days_back=90
)

print(f"Analysis Period: {stats['analysis_period']['days_analyzed']} days")
print(f"Sensor: {stats['product_info']['sensor']}")
```

## Key Applications

### Agriculture
- **Irrigation scheduling and optimization**: Optimize water usage based on actual soil moisture
- **Crop stress monitoring**: Detect water stress before visible symptoms appear
- **Yield prediction modeling**: Incorporate soil moisture into yield forecasting models
- **Field condition assessment**: Evaluate field conditions for planting and harvesting

### Water Management
- **Drought monitoring and early warning**: Track drought development and severity
- **Water resource planning**: Support water allocation and conservation decisions
- **Reservoir management**: Optimize water storage and release schedules
- **Flood risk assessment**: Monitor soil saturation for flood prediction

### Environmental Monitoring
- **Ecosystem health monitoring**: Assess vegetation stress and ecosystem conditions
- **Climate change research**: Study long-term soil moisture trends
- **Carbon cycle studies**: Understand soil-atmosphere carbon exchange
- **Wildfire risk assessment**: Monitor dry soil conditions that increase fire risk

### Disaster Management
- **Natural disaster risk assessment**: Evaluate conditions for various natural hazards
- **Emergency response planning**: Support disaster preparedness and response
- **Recovery monitoring**: Track post-disaster recovery progress
- **Insurance risk modeling**: Assess agricultural and environmental risks

## Data Characteristics

- **Measurement**: Soil water content (volumetric water content)
- **Units**: m³/m³ (cubic meters of water per cubic meter of soil)
- **Temporal Resolution**: Near-daily global coverage
- **Spatial Coverage**: Global
- **Data Format**: GeoTIFF files
- **Delivery Method**: Cloud storage (GCS, AWS, Azure) via Subscriptions API

## Setup Requirements

### Environment Variables
```bash
export PLANET_API_KEY="your_planet_api_key_here"
```

### Planet Account
- Active Planet account with subscription access
- Appropriate quota allocation for SWC products
- Cloud storage credentials (for data delivery)

### Cloud Storage
For actual data delivery, you'll need:
- Cloud storage bucket (Google Cloud Storage, AWS S3, or Azure)
- Proper authentication credentials for cloud provider
- Sufficient storage capacity for data volumes

## API Integration

The tool integrates with Planet's Subscriptions API:

- **Base URL**: `https://api.planet.com/subscriptions/v1`
- **Authentication**: Bearer token using Planet API key
- **Rate Limits**: 5 requests per second for subscription operations
- **Data Delivery**: Automated to configured cloud storage

## Error Handling

The tool includes comprehensive error handling for:
- Invalid resolution or sensor parameters
- Missing API keys or credentials
- Network connectivity issues
- API rate limiting
- Invalid geographic coordinates

## Limitations and Notes

1. **Subscription Required**: Actual soil water content data requires an active Planet subscription
2. **Cloud Storage**: Data delivery requires configured cloud storage credentials
3. **Processing Time**: Subscription data may take time to process and deliver
4. **Quota Limits**: Planet enforces quota limits on data volume and active subscriptions
5. **Geographic Coverage**: While global, data quality may vary by region and season

## Best Practices

1. **Start Small**: Begin with smaller areas and shorter time periods to understand data volumes
2. **Monitor Quotas**: Track subscription usage against available quotas
3. **Validate Locations**: Ensure geographic coordinates are within expected ranges
4. **Consider Resolution**: Choose appropriate resolution based on application needs
5. **Plan Storage**: Ensure adequate cloud storage capacity for expected data volumes
6. **Combine Data**: Integrate SWC data with weather and crop information for comprehensive analysis

## Support and Resources

- **Planet Documentation**: [docs.planet.com](https://docs.planet.com/data/planetary-variables/soil-water-content/)
- **Planet University**: Training resources and tutorials
- **GitHub Notebooks**: [Planet Labs Notebooks](https://github.com/planetlabs/notebooks)
- **API Reference**: [Subscriptions API Documentation](https://docs.planet.com/develop/apis/subscriptions/)

## Example Output

When you call `tool_get_soil_water_content()`, you'll receive a comprehensive response like this:

```json
{
  "location": {
    "latitude": 41.5868,
    "longitude": -93.625,
    "geometry": { ... }
  },
  "product_info": {
    "id": "SWC-SMAP-L_V1.0_100",
    "sensor": "SMAP",
    "resolution": "100m",
    "description": "Soil Water Content data from SMAP sensor at 100m resolution"
  },
  "data_characteristics": {
    "measurement": "Soil water content (volumetric water content)",
    "units": "m³/m³",
    "temporal_resolution": "Near-daily",
    "spatial_resolution": "100m",
    "sensor_type": "SMAP",
    "coverage": "Global"
  },
  "use_cases": [
    "Agricultural irrigation planning",
    "Drought monitoring and assessment",
    "Water resource management",
    "Natural disaster risk assessment",
    "Crop yield prediction"
  ],
  "status": "subscription_required"
}
```

This tool provides a powerful foundation for integrating satellite-based soil water content monitoring into agricultural and environmental applications.
