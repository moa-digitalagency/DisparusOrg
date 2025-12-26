import { useState, useEffect, useRef } from "react";
import { WifiOff, Wifi } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showBanner, setShowBanner] = useState(false);
  const { t } = useI18n();
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const debouncedUpdate = (online: boolean) => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
      debounceTimer.current = setTimeout(() => {
        setIsOnline(online);
        setShowBanner(true);
        if (online) {
          setTimeout(() => setShowBanner(false), 3000);
        }
      }, 500);
    };

    const handleOnline = () => debouncedUpdate(true);
    const handleOffline = () => debouncedUpdate(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  if (!showBanner && isOnline) return null;

  return (
    <div
      className={`fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
        isOnline
          ? "bg-green-600 text-white"
          : "bg-amber-600 text-white"
      }`}
      role="status"
      aria-live="polite"
      data-testid="offline-indicator"
    >
      <div className="flex items-center gap-3">
        {isOnline ? (
          <Wifi className="w-5 h-5 shrink-0" />
        ) : (
          <WifiOff className="w-5 h-5 shrink-0" />
        )}
        <div>
          <p className="font-medium">
            {isOnline ? "Reconnected" : t("offline.title")}
          </p>
          {!isOnline && (
            <p className="text-sm opacity-90">{t("offline.message")}</p>
          )}
        </div>
      </div>
    </div>
  );
}
