import re
from typing import Optional, Tuple
import googlemaps
from core.models import GoogleMapsConfig


class GeocodingService:
    """Service for geocoding addresses to lat/lon"""
    
    def __init__(self):
        config = GoogleMapsConfig.load()
        self.api_key = config.api_key if config and config.api_key else ""
        self.client = None
        if self.api_key:
            try:
                self.client = googlemaps.Client(key=self.api_key)
            except Exception:
                pass
    
    def _sanitize_address(self, addr: str) -> str:
        """Clean address string"""
        if not addr:
            return ""
        s = re.sub(r"[\r\n\t]+", " ", addr).strip()
        s = re.sub(r"\s{2,}", " ", s).strip(",;.")
        return s
    
    def _ensure_country_suffix(self, addr: str) -> str:
        """Add country suffix if missing"""
        if not addr:
            return addr
        low = addr.lower()
        if any(c in low for c in [" melbourne", ", victoria", ", vic", " australia"]):
            return addr
        # Restrict to Melbourne for this app
        return addr + ", Melbourne, VIC, Australia"
    
    def geocode(self, address: str) -> Tuple[Optional[Tuple[float, float]], str]:
        """Geocode address using multiple methods"""
        if not self.api_key:
            return None, "Missing API key"
        if not address or not str(address).strip():
            return None, "Empty address"
        
        if not self.client:
            return None, "GM client not initialized"
        
        addr = self._sanitize_address(address)
        if not addr:
            return None, "Address empty"
        
        # Try Places Autocomplete
        try:
            preds = self.client.places_autocomplete(input_text=addr, types="geocode")
            if preds:
                pid = preds[0].get("place_id")
                if pid:
                    det = self.client.place(place_id=pid, fields=["geometry"])
                    loc = det.get("result", {}).get("geometry", {}).get("location")
                    if loc:
                        return (float(loc["lat"]), float(loc["lng"])), "places_details"
        except Exception as e:
            last_err = f"autocomplete/details: {e}"
        
        # Try Geocoding API
        try:
            aug = self._ensure_country_suffix(addr)
            res = self.client.geocode(aug)
            if res and res[0].get("geometry", {}).get("location"):
                loc = res[0]["geometry"]["location"]
                return (float(loc["lat"]), float(loc["lng"])), "geocode"
        except Exception as e:
            last_err = f"geocode: {e}"
        
        # Try Places Text Search
        try:
            ts = self.client.places(addr)
            results = ts.get("results", []) if isinstance(ts, dict) else []
            if results:
                loc = results[0].get("geometry", {}).get("location")
                if loc:
                    return (float(loc["lat"]), float(loc["lng"])), "places_text"
        except Exception as e:
            last_err = f"places text: {e}"
        
        return None, last_err if 'last_err' in locals() else "ZERO_RESULTS"
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Reverse geocode coordinates to address"""
        if not self.client:
            return None
        try:
            result = self.client.reverse_geocode((lat, lon))
            if result:
                return result[0].get('formatted_address')
        except Exception:
            pass
        return None


class DirectionsService:
    """Service for getting directions and polylines"""
    
    def __init__(self):
        config = GoogleMapsConfig.load()
        self.api_key = config.api_key if config and config.api_key else ""
        self.client = None
        if self.api_key:
            try:
                self.client = googlemaps.Client(key=self.api_key)
            except Exception:
                pass
    
    def get_polyline(self, origin: Tuple[float, float], destination: Tuple[float, float], 
                     waypoints: Optional[list] = None) -> Optional[list]:
        """Get polyline for route"""
        if not self.client:
            return None
        
        try:
            o = {"lat": origin[0], "lng": origin[1]}
            d = {"lat": destination[0], "lng": destination[1]}
            wps = [{"lat": lat, "lng": lon} for (lat, lon) in waypoints] if waypoints else None
            
            res = self.client.directions(origin=o, destination=d, waypoints=wps, mode="driving")
            if not res:
                return None
            
            from googlemaps.convert import decode_polyline
            path = []
            
            if "overview_polyline" in res[0] and res[0]["overview_polyline"]:
                path = decode_polyline(res[0]["overview_polyline"]["points"])
            else:
                for leg in res[0].get("legs", []):
                    for step in leg.get("steps", []):
                        path.extend(decode_polyline(step["polyline"]["points"]))
            
            return [[pt["lng"], pt["lat"]] for pt in path] if path else None
        except Exception:
            return None


class DistanceService:
    """Service for calculating distances and travel times"""
    
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km using Haversine formula"""
        import math
        R = 6371.0088  # Earth radius in km
        p = math.pi / 180
        
        dlat = (lat2 - lat1) * p
        dlon = (lon2 - lon1) * p
        
        a = 0.5 - math.cos(dlat) / 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * (1 - math.cos(dlon)) / 2
        return 2 * R * math.asin(math.sqrt(a))
    
    @staticmethod
    def travel_minutes(lat1: float, lon1: float, lat2: float, lon2: float, kph: float = 40.0) -> float:
        """Calculate travel time in minutes"""
        dist = DistanceService.haversine_km(lat1, lon1, lat2, lon2)
        hrs = dist / max(kph, 1e-6)
        return 60.0 * hrs


# Alias for backward compatibility
GoogleMapsService = GeocodingService
haversine_km = DistanceService.haversine_km

