import os
import requests
import time
import json


# utility function to extract open meteo data
# requires aviation hub coordinates already defined

def extract_meteo_data(coordinates: list[tuple], airport_codes: list[str], output_dir: str = None):
    print("starting data extraction...")
    
    if output_dir is None:
        # Default fallback output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw", "meteo")
        
    os.makedirs(output_dir, exist_ok=True)

    meteo_results = []
    for coordinate, airport_code in zip(coordinates, airport_codes):

        curr_latitude = coordinate[0]
        curr_longitude = coordinate[1]

        # url query parameters are already predetermined and consistent
        meteo_url = (
            f"https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={curr_latitude}"
            f"&longitude={curr_longitude}"
            f"&start_date=2025-01-01"
            f"&end_date=2025-12-31"
            f"&daily=temperature_2m_mean,weather_code,"
            f"temperature_2m_max,temperature_2m_min,"
            f"precipitation_sum,rain_sum,snowfall_sum,"
            f"wind_speed_10m_max,wind_gusts_10m_max,"
            f"sunshine_duration"
            f"&hourly=temperature_2m,snowfall,snow_depth,"
            f"rain,relative_humidity_2m,precipitation,"
            f"pressure_msl,wind_speed_100m,"
            f"wind_direction_100m,cloud_cover,"
            f"dew_point_2m"
            f"&timezone=auto"
        )

        try:
            # avoid rate limiting
            time.sleep(1.5)

            # request data
            response = requests.get(
                meteo_url,
                timeout=30
            )

            # debugging for raise error for bad status codes
            response.raise_for_status()

            # parse json
            meteo_json = response.json()
            
            # append metadata
            meteo_json["airport_code"] = airport_code
            meteo_json["latitude"] = curr_latitude
            meteo_json["longitude"] = curr_longitude
            
            # save to json
            json_filename = f"{airport_code}_meteo_2025.json"
            json_path = os.path.join(output_dir, json_filename)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(meteo_json, f, indent=4)
                
            print(f"Saved {json_filename}")

            record = {
                "airport_code": airport_code,
                "latitude": curr_latitude,
                "longitude": curr_longitude,
                "status_code": response.status_code,
                "success": True
            }

        # error handling for failed requests
        except requests.exceptions.RequestException as e:

            record = {
                "airport_code": airport_code,
                "latitude": curr_latitude,
                "longitude": curr_longitude,
                "success": False,
                "error": str(e)
            }

        meteo_results.append(record)

    print("Data extraction complete.")

    return meteo_results


def main():
    print("extracting data from Open Meteo API")

    # test one
    res = extract_meteo_data([(52.52, 13.41)], ["EDDB"])

    print(res)


if __name__ == "__main__":
    main()

