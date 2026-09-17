"""
System-Metriken des Raspberry Pi 5: CPU, RAM, Disk, Temperatur, Uptime.
"""
import time
import psutil

from app.config import get_settings
from app.schemas import SystemMetrics

settings = get_settings()
_BOOT_TIME = psutil.boot_time()


def _read_pi_temperature() -> float | None:
    try:
        with open(settings.RASPBERRY_PI_THERMAL_ZONE, "r") as fh:
            raw = fh.read().strip()
            return round(int(raw) / 1000.0, 1)
    except (FileNotFoundError, ValueError):
        pass
    # Fallback: psutil sensors (funktioniert je nach Kernel/Board)
    try:
        temps = psutil.sensors_temperatures()
        for key in ("cpu_thermal", "cpu-thermal", "soc_thermal"):
            if key in temps and temps[key]:
                return round(temps[key][0].current, 1)
    except (AttributeError, OSError):
        pass
    return None


def get_system_metrics() -> SystemMetrics:
    cpu_percent = psutil.cpu_percent(interval=0.3)
    vmem = psutil.virtual_memory()
    disk = psutil.disk_usage(settings.DISK_PATH)

    return SystemMetrics(
        cpu_percent=cpu_percent,
        memory_percent=vmem.percent,
        memory_used_mb=round(vmem.used / (1024 ** 2), 1),
        memory_total_mb=round(vmem.total / (1024 ** 2), 1),
        disk_percent=disk.percent,
        disk_used_gb=round(disk.used / (1024 ** 3), 2),
        disk_total_gb=round(disk.total / (1024 ** 3), 2),
        temperature_celsius=_read_pi_temperature(),
        host_uptime_seconds=int(time.time() - _BOOT_TIME),
    )
