"""
Soil Water Content tool for accessing Planet's soil water content data

This module provides access to Planet's Soil Water Content (SWC) data through the Subscriptions API:
- Current and historical soil water content measurements
- Multiple spatial resolutions (20m, 100m, 1000m)
- Subscription management for continuous data delivery
- Statistical analysis of soil water content over time

Functions:
- tool_get_soil_water_content: Get current soil water content for a location
- tool_create_swc_subscription: Create a subscription for continuous SWC data delivery
- tool_get_swc_statistics: Get statistical analysis of soil water content over time
- tool_get_swc_product_info: Get information about available SWC products

Requires PLANET_API_KEY environment variable to be set.
"""
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ...config import get_logger
import dotenv

dotenv.load_dotenv()

# Initialize logger
logger = get_logger(__name__)

PLANET_API_KEY = os.getenv("PLANET_API_KEY")

# Planet API endpoints
SUBSCRIPTIONS_API_BASE = "https://api.planet.com/subscriptions/v1"

# Available SWC product IDs based on Planet documentation
SWC_PRODUCTS = {
    "20m": {
        "smap": "SWC-SMAP-L_V1.0_20",
        "amsr2": "SWC-AMSR2-X_V5.0_20"
    },
    "100m": {
        "smap": "SWC-SMAP-L_V1.0_100", 
        "amsr2": "SWC-AMSR2-X_V5.0_100"
    },
    "1000m": {
        "smap": "SWC-SMAP-L_V1.0_1000",
        "amsr2": "SWC-AMSR2-X_V5.0_1000"
    }
}

def tool_get_soil_water_content(lat: float, lon: float, resolution: str = "100m", 
                               sensor: str = "smap", days_back: int = 30) -> Dict:
    """
    Get soil water content data for a specific location.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        resolution (str): Spatial resolution - "20m", "100m", or "1000m" (default: "100m")
        sensor (str): Sensor type - "smap" or "amsr2" (default: "smap")
        days_back (int): Number of days to look back for data (default: 30)
    
    Returns:
        Dict: Soil water content information and metadata
    """
    logger.info(f"Getting soil water content data for coordinates: {lat}, {lon}")
    
    if not PLANET_API_KEY:
        logger.error("PLANET_API_KEY is not set in environment variables")
        return {"error": "PLANET_API_KEY is not set in environment variables"}
    
    # Validate inputs
    if resolution not in SWC_PRODUCTS:
        logger.error(f"Invalid resolution: {resolution}. Must be one of: {list(SWC_PRODUCTS.keys())}")
        return {"error": f"Invalid resolution: {resolution}. Must be one of: {list(SWC_PRODUCTS.keys())}"}
    
    if sensor not in SWC_PRODUCTS[resolution]:
        logger.error(f"Invalid sensor: {sensor}. Must be one of: {list(SWC_PRODUCTS[resolution].keys())}")
        return {"error": f"Invalid sensor: {sensor}. Must be one of: {list(SWC_PRODUCTS[resolution].keys())}"}
    
    try:
        # Get the product ID
        product_id = SWC_PRODUCTS[resolution][sensor]
        
        # Create a small area of interest around the point (approximately 1km buffer)
        buffer = 0.009  # Roughly 1km at equator
        geometry = {
            "type": "Polygon",
            "coordinates": [[
                [lon - buffer, lat - buffer],
                [lon + buffer, lat - buffer], 
                [lon + buffer, lat + buffer],
                [lon - buffer, lat + buffer],
                [lon - buffer, lat - buffer]
            ]]
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Create subscription request for historical data
        subscription_request = {
            "name": f"SWC Query {lat},{lon} {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source": {
                "type": "soil_water_content",
                "parameters": {
                    "id": product_id,
                    "geometry": geometry,
                    "start_time": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end_time": end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            },
            "delivery": {
                "type": "cloud",
                "archive_type": "zip",
                "cloud_config": {
                    "provider": "gcs",
                    "bucket": "temp-swc-data",
                    "credentials": None  # Would need proper cloud credentials
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {PLANET_API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"Making request to Planet Subscriptions API")
        logger.debug(f"Request payload: {subscription_request}")
        
        # Note: This is a simplified example. In practice, you'd need:
        # 1. Proper cloud storage credentials
        # 2. Subscription monitoring
        # 3. Data processing pipeline
        
        # For now, return information about what would be available
        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "geometry": geometry
            },
            "product_info": {
                "id": product_id,
                "sensor": sensor.upper(),
                "resolution": resolution,
                "description": f"Soil Water Content data from {sensor.upper()} sensor at {resolution} resolution"
            },
            "query_parameters": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days_requested": days_back
            },
            "data_characteristics": {
                "measurement": "Soil water content (volumetric water content)",
                "units": "m³/m³ (cubic meters of water per cubic meter of soil)",
                "temporal_resolution": "Near-daily",
                "spatial_resolution": resolution,
                "sensor_type": sensor.upper(),
                "coverage": "Global"
            },
            "use_cases": [
                "Agricultural irrigation planning",
                "Drought monitoring and assessment", 
                "Water resource management",
                "Natural disaster risk assessment",
                "Crop yield prediction"
            ],
            "status": "subscription_required",
            "note": "To access actual soil water content data, you would need to create a Planet subscription and configure cloud storage delivery. This tool shows the available products and subscription parameters."
        }
        
        logger.info(f"Successfully retrieved SWC product information for {lat}, {lon}")
        return result
        
    except requests.RequestException as e:
        logger.error(f"Network error calling Planet API: {str(e)}")
        return {"error": f"Network error calling Planet API: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error: {str(e)}"}


def tool_create_swc_subscription(lat: float, lon: float, resolution: str = "100m",
                                sensor: str = "smap", cloud_provider: str = "gcs",
                                bucket_name: str = None, start_date: str = None, 
                                end_date: str = None) -> Dict:
    """
    Create a subscription for continuous soil water content data delivery.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees  
        resolution (str): Spatial resolution - "20m", "100m", or "1000m"
        sensor (str): Sensor type - "smap" or "amsr2"
        cloud_provider (str): Cloud provider - "gcs", "aws", "azure"
        bucket_name (str): Cloud storage bucket name
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
    
    Returns:
        Dict: Subscription creation response and details
    """
    logger.info(f"Creating SWC subscription for coordinates: {lat}, {lon}")
    
    if not PLANET_API_KEY:
        logger.error("PLANET_API_KEY is not set in environment variables")
        return {"error": "PLANET_API_KEY is not set in environment variables"}
    
    if not bucket_name:
        logger.error("Cloud storage bucket name is required for subscription")
        return {"error": "Cloud storage bucket name is required for subscription"}
    
    try:
        # Get the product ID
        product_id = SWC_PRODUCTS[resolution][sensor]
        
        # Create area of interest (1km buffer around point)
        buffer = 0.009
        geometry = {
            "type": "Polygon", 
            "coordinates": [[
                [lon - buffer, lat - buffer],
                [lon + buffer, lat - buffer],
                [lon + buffer, lat + buffer], 
                [lon - buffer, lat + buffer],
                [lon - buffer, lat - buffer]
            ]]
        }
        
        # Set date range
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        
        subscription_request = {
            "name": f"SWC Subscription {lat},{lon} {datetime.now().strftime('%Y%m%d')}",
            "source": {
                "type": "soil_water_content",
                "parameters": {
                    "id": product_id,
                    "geometry": geometry,
                    "start_time": f"{start_date}T00:00:00Z",
                    "end_time": f"{end_date}T23:59:59Z"
                }
            },
            "delivery": {
                "type": "cloud",
                "archive_type": "zip",
                "cloud_config": {
                    "provider": cloud_provider,
                    "bucket": bucket_name
                }
            }
        }
        
        result = {
            "subscription_request": subscription_request,
            "product_info": {
                "id": product_id,
                "sensor": sensor.upper(),
                "resolution": resolution
            },
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "delivery_info": {
                "cloud_provider": cloud_provider,
                "bucket": bucket_name,
                "format": "GeoTIFF files in ZIP archives"
            },
            "status": "ready_to_submit",
            "note": "This subscription request is ready to be submitted to Planet's Subscriptions API. You would need proper cloud storage credentials and quota to activate it."
        }
        
        logger.info(f"Successfully prepared SWC subscription for {lat}, {lon}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}", exc_info=True)
        return {"error": f"Error creating subscription: {str(e)}"}


def tool_get_swc_statistics(lat: float, lon: float, resolution: str = "100m",
                          sensor: str = "smap", days_back: int = 90) -> Dict:
    """
    Get statistical analysis of soil water content over time for a location.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        resolution (str): Spatial resolution - "20m", "100m", or "1000m"
        sensor (str): Sensor type - "smap" or "amsr2"
        days_back (int): Number of days to analyze (default: 90)
    
    Returns:
        Dict: Statistical analysis of soil water content trends
    """
    logger.info(f"Getting SWC statistics for coordinates: {lat}, {lon}")
    
    try:
        product_id = SWC_PRODUCTS[resolution][sensor]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Simulate statistical analysis (in real implementation, this would process actual data)
        result = {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "analysis_period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days_analyzed": days_back
            },
            "product_info": {
                "id": product_id,
                "sensor": sensor.upper(),
                "resolution": resolution
            },
            "statistical_metrics": {
                "note": "Actual statistics would be computed from subscription data",
                "typical_metrics": [
                    "Mean soil water content",
                    "Standard deviation",
                    "Minimum and maximum values",
                    "Trend analysis (increasing/decreasing)",
                    "Seasonal patterns",
                    "Drought risk indicators"
                ]
            },
            "interpretation": {
                "agricultural_insights": [
                    "Irrigation needs assessment",
                    "Crop stress risk evaluation", 
                    "Optimal planting time identification"
                ],
                "environmental_insights": [
                    "Drought conditions monitoring",
                    "Flood risk assessment",
                    "Ecosystem health indicators"
                ]
            },
            "recommendations": {
                "data_access": "Set up a Planet subscription to access historical SWC data",
                "analysis_tools": "Use statistical analysis tools to process time series data",
                "monitoring": "Establish regular monitoring intervals for trend detection"
            }
        }
        
        logger.info(f"Successfully generated SWC statistics overview for {lat}, {lon}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}", exc_info=True)
        return {"error": f"Error generating statistics: {str(e)}"}


def tool_get_swc_product_info() -> Dict:
    """
    Get information about available soil water content products and capabilities.
    
    Returns:
        Dict: Comprehensive information about SWC products and services
    """
    logger.info("Getting SWC product information")
    
    try:
        result = {
            "service_overview": {
                "name": "Planet Soil Water Content (SWC)",
                "description": "Near-daily global soil water content measurements from satellite sensors",
                "provider": "Planet Labs",
                "data_source": "Passive microwave observations"
            },
            "available_products": SWC_PRODUCTS,
            "product_details": {
                "spatial_resolutions": {
                    "20m": "High resolution for field-level analysis",
                    "100m": "Balanced resolution for regional monitoring", 
                    "1000m": "Lower resolution for large-scale analysis"
                },
                "sensors": {
                    "SMAP": "Soil Moisture Active Passive mission",
                    "AMSR2": "Advanced Microwave Scanning Radiometer 2"
                },
                "temporal_coverage": "Near-daily global coverage",
                "measurement_units": "m³/m³ (volumetric water content)",
                "data_format": "GeoTIFF"
            },
            "key_applications": {
                "agriculture": [
                    "Irrigation scheduling and optimization",
                    "Crop stress monitoring",
                    "Yield prediction modeling",
                    "Field condition assessment"
                ],
                "water_management": [
                    "Drought monitoring and early warning",
                    "Water resource planning", 
                    "Reservoir management",
                    "Flood risk assessment"
                ],
                "environmental": [
                    "Ecosystem health monitoring",
                    "Climate change research",
                    "Carbon cycle studies",
                    "Wildfire risk assessment"
                ],
                "disaster_management": [
                    "Natural disaster risk assessment",
                    "Emergency response planning",
                    "Recovery monitoring",
                    "Insurance risk modeling"
                ]
            },
            "access_methods": {
                "subscriptions_api": {
                    "description": "Automated continuous data delivery",
                    "suitable_for": "Operational monitoring and analysis",
                    "delivery_options": ["Cloud storage", "API access"]
                },
                "planet_platform": {
                    "description": "Interactive data exploration and download",
                    "suitable_for": "Research and ad-hoc analysis"
                }
            },
            "data_characteristics": {
                "accuracy": "Strong correlation with ground-based measurements",
                "consistency": "Uniform global coverage and processing",
                "reliability": "Weather-independent passive microwave observations",
                "archive": "Historical data available for long-term analysis"
            },
            "integration_benefits": {
                "cost_effective": "Alternative to dense sensor networks",
                "scalable": "Global coverage without infrastructure requirements",
                "timely": "Near real-time data availability",
                "comprehensive": "Consistent global monitoring capability"
            }
        }
        
        logger.info("Successfully retrieved SWC product information")
        return result
        
    except Exception as e:
        logger.error(f"Error getting product info: {str(e)}", exc_info=True)
        return {"error": f"Error getting product info: {str(e)}"}


def tool_analyze_soil_conditions(lat: float, lon: float, crop_type: str = None,
                                season: str = None, resolution: str = "100m") -> Dict:
    """
    Analyze soil water conditions for agricultural decision making.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees
        crop_type (str): Type of crop being analyzed (optional)
        season (str): Growing season (spring, summer, fall, winter) (optional)
        resolution (str): Spatial resolution for analysis
    
    Returns:
        Dict: Agricultural insights based on soil water content analysis
    """
    logger.info(f"Analyzing soil conditions for agriculture at {lat}, {lon}")
    
    try:
        # Get current season if not provided
        if not season:
            month = datetime.now().month
            if month in [12, 1, 2]:
                season = "winter"
            elif month in [3, 4, 5]:
                season = "spring"
            elif month in [6, 7, 8]:
                season = "summer"
            else:
                season = "fall"
        
        result = {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "analysis_parameters": {
                "crop_type": crop_type or "general",
                "season": season,
                "resolution": resolution,
                "analysis_date": datetime.now().strftime("%Y-%m-%d")
            },
            "soil_water_assessment": {
                "current_status": "Analysis requires active SWC subscription",
                "typical_indicators": {
                    "optimal_range": "Field capacity (25-50% depending on soil type)",
                    "stress_threshold": "Below permanent wilting point (~15%)",
                    "saturation_level": "Above field capacity (potential drainage issues)"
                }
            },
            "agricultural_recommendations": {
                "irrigation_guidance": {
                    "general": "Monitor soil water content relative to crop water requirements",
                    "spring": "Assess soil moisture for optimal planting conditions",
                    "summer": "Monitor for drought stress and irrigation needs",
                    "fall": "Evaluate soil conditions for harvest timing",
                    "winter": "Monitor for frost protection and drainage needs"
                },
                "crop_specific_insights": {
                    "note": f"Recommendations tailored for {crop_type or 'general crops'}",
                    "water_requirements": "Vary by crop type and growth stage",
                    "critical_periods": "Flowering and fruit development stages most sensitive"
                }
            },
            "risk_assessment": {
                "drought_risk": "Evaluate using historical SWC trends",
                "flood_risk": "Monitor excessive soil saturation",
                "disease_risk": "High soil moisture can increase fungal diseases",
                "yield_impact": "Optimal soil moisture critical for maximum yield"
            },
            "monitoring_recommendations": {
                "frequency": "Daily monitoring during critical growth periods",
                "thresholds": "Set alerts for irrigation and stress conditions",
                "integration": "Combine with weather forecasts and crop models",
                "validation": "Calibrate with ground-based soil sensors when available"
            },
            "data_requirements": {
                "subscription_needed": "Active Planet SWC subscription required",
                "historical_data": "Recommended for establishing baseline conditions",
                "real_time_access": "Essential for timely agricultural decisions"
            }
        }
        
        logger.info(f"Successfully generated agricultural soil analysis for {lat}, {lon}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing soil conditions: {str(e)}", exc_info=True)
        return {"error": f"Error analyzing soil conditions: {str(e)}"}
