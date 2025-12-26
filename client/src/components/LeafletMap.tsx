import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Button } from "@/components/ui/button";
import { MapPin, Navigation, Loader2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface LeafletMapProps {
  center?: [number, number];
  zoom?: number;
  height?: string;
  markers?: Array<{
    lat: number;
    lng: number;
    popup?: string;
    photoUrl?: string;
    id?: string;
    name?: string;
  }>;
  onClick?: (lat: number, lng: number) => void;
  selectedPosition?: [number, number] | null;
  showGeolocation?: boolean;
  className?: string;
}

export function LeafletMap({
  center = [7.3697, 12.3547], // Central Africa
  zoom = 4,
  height = "h-96",
  markers = [],
  onClick,
  selectedPosition,
  showGeolocation = true,
  className = "",
}: LeafletMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);
  const selectedMarkerRef = useRef<L.Marker | null>(null);
  const [isLocating, setIsLocating] = useState(false);
  const { t } = useI18n();

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    const map = L.map(mapRef.current).setView(center, zoom);
    
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    if (onClick) {
      map.on("click", (e) => {
        onClick(e.latlng.lat, e.latlng.lng);
      });
    }

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    markers.forEach((marker) => {
      const icon = marker.photoUrl
        ? L.divIcon({
            className: "custom-marker",
            html: `<div class="w-10 h-10 rounded-full border-2 border-white shadow-lg overflow-hidden bg-muted">
              <img src="${marker.photoUrl}" alt="" class="w-full h-full object-cover" />
            </div>`,
            iconSize: [40, 40],
            iconAnchor: [20, 40],
          })
        : L.divIcon({
            className: "custom-marker",
            html: `<div class="w-8 h-8 rounded-full bg-destructive border-2 border-white shadow-lg flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 32],
          });

      const m = L.marker([marker.lat, marker.lng], { icon }).addTo(map);
      
      if (marker.popup || marker.name) {
        m.bindPopup(
          marker.popup || 
          `<div class="text-center">
            <strong>${marker.name || ""}</strong>
            ${marker.id ? `<br/><span class="text-xs text-muted-foreground">ID: ${marker.id}</span>` : ""}
          </div>`
        );
      }

      markersRef.current.push(m);
    });
  }, [markers]);

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (selectedMarkerRef.current) {
      selectedMarkerRef.current.remove();
      selectedMarkerRef.current = null;
    }

    if (selectedPosition) {
      const icon = L.divIcon({
        className: "selected-marker",
        html: `<div class="w-8 h-8 rounded-full bg-primary border-2 border-white shadow-lg flex items-center justify-center animate-pulse">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
        </div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
      });

      selectedMarkerRef.current = L.marker(selectedPosition, { icon }).addTo(map);
      map.setView(selectedPosition, Math.max(map.getZoom(), 12));
    }
  }, [selectedPosition]);

  const handleGeolocation = () => {
    if (!navigator.geolocation) return;
    
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        if (onClick) {
          onClick(latitude, longitude);
        }
        if (mapInstanceRef.current) {
          mapInstanceRef.current.setView([latitude, longitude], 14);
        }
        setIsLocating(false);
      },
      () => {
        setIsLocating(false);
      },
      { enableHighAccuracy: true }
    );
  };

  return (
    <div className={`relative ${className}`}>
      <div ref={mapRef} className={`${height} w-full rounded-lg z-0`} />
      {showGeolocation && (
        <div className="absolute top-2 right-2 z-10">
          <Button
            type="button"
            size="icon"
            variant="secondary"
            onClick={handleGeolocation}
            disabled={isLocating}
            data-testid="button-geolocation"
          >
            {isLocating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Navigation className="w-4 h-4" />
            )}
          </Button>
        </div>
      )}
      {selectedPosition && (
        <div className="absolute bottom-2 left-2 z-10 bg-background/90 backdrop-blur-sm px-3 py-1.5 rounded-md text-sm flex items-center gap-2">
          <MapPin className="w-4 h-4 text-primary" />
          <span>{selectedPosition[0].toFixed(4)}, {selectedPosition[1].toFixed(4)}</span>
        </div>
      )}
    </div>
  );
}
