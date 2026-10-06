"""
Smart Energy Metering and Real-Time Electricity Consumption Monitoring System
Main Module: IoT-Based Energy Consumption Simulation and Monitoring

This module implements a comprehensive IoT-based energy metering system that simulates
real-time electricity consumption monitoring, anomaly detection, and cost estimation.

Author: Internship Project Team
Date: 2024
"""

import json
import random
import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MeterStatus(Enum):
    """Enumeration for smart meter status"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    FAULTY = "Faulty"
    MAINTENANCE = "Maintenance"
    DISCONNECTED = "Disconnected"


class ConsumptionLevel(Enum):
    """Enumeration for consumption levels"""
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"


class AnomalyType(Enum):
    """Types of consumption anomalies"""
    SPIKE = "Spike"
    SUDDEN_DROP = "Sudden Drop"
    SUSTAINED_HIGH = "Sustained High"
    ZERO_CONSUMPTION = "Zero Consumption"
    VOLTAGE_FLUCTUATION = "Voltage Fluctuation"


@dataclass
class EnergyReading:
    """Data class representing a single energy reading"""
    meter_id: str
    timestamp: datetime.datetime
    voltage: float  # Volts (200-240V typical)
    current: float  # Amperes
    power: float  # Watts (Voltage * Current)
    energy_consumed: float  # kWh
    frequency: float  # Hz (50 or 60)
    power_factor: float  # 0.0 to 1.0
    consumption_level: ConsumptionLevel
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'meter_id': self.meter_id,
            'timestamp': self.timestamp.isoformat(),
            'voltage': round(self.voltage, 2),
            'current': round(self.current, 2),
            'power': round(self.power, 2),
            'energy_consumed': round(self.energy_consumed, 4),
            'frequency': round(self.frequency, 2),
            'power_factor': round(self.power_factor, 3),
            'consumption_level': self.consumption_level.value
        }


@dataclass
class EnergyAlert:
    """Data class representing an energy alert"""
    alert_id: str
    meter_id: str
    alert_type: str  # 'ANOMALY', 'FAULT', 'HIGH_CONSUMPTION', 'VOLTAGE_ISSUE'
    severity: str  # 'INFO', 'WARNING', 'CRITICAL'
    message: str
    timestamp: datetime.datetime
    resolved: bool = False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'meter_id': self.meter_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved
        }


@dataclass
class BillingRecord:
    """Data class for billing information"""
    meter_id: str
    period_start: datetime.datetime
    period_end: datetime.datetime
    total_energy_kwh: float
    rate_per_kwh: float  # Currency units per kWh
    total_amount: float
    peak_hour_units: float
    off_peak_units: float
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'meter_id': self.meter_id,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_energy_kwh': round(self.total_energy_kwh, 2),
            'rate_per_kwh': round(self.rate_per_kwh, 2),
            'total_amount': round(self.total_amount, 2),
            'peak_hour_units': round(self.peak_hour_units, 2),
            'off_peak_units': round(self.off_peak_units, 2)
        }


class SmartEnergyMeter:
    """Class representing a smart energy meter"""
    
    def __init__(self, meter_id: str, location: str, meter_type: str = "Residential"):
        """
        Initialize a smart energy meter
        
        Args:
            meter_id: Unique meter identifier
            location: Physical location of the meter
            meter_type: Type of meter (Residential, Commercial, Industrial)
        """
        self.meter_id = meter_id
        self.location = location
        self.meter_type = meter_type
        self.status = MeterStatus.ACTIVE
        self.readings: List[EnergyReading] = []
        self.alerts: List[EnergyAlert] = []
        self.total_energy_consumed = 0.0  # kWh
        self.last_reading = None
        self.installation_date = datetime.datetime.now()
        self.firmware_version = "2.1.0"
    
    def take_reading(self, hour_of_day: int = 12, day_type: str = "weekday") -> EnergyReading:
        """
        Take an energy reading from the meter
        
        Args:
            hour_of_day: Hour of the day (0-23)
            day_type: Type of day (weekday, weekend, holiday)
            
        Returns:
            EnergyReading object
        """
        timestamp = datetime.datetime.now()
        
        # Generate voltage reading (nominal 230V with small variations)
        voltage = 230 + random.gauss(0, 3)
        voltage = max(200, min(240, voltage))  # Clamp to valid range
        
        # Generate current based on time of day and day type
        current = self._generate_current(hour_of_day, day_type)
        
        # Calculate power (P = V * I * PF)
        power_factor = 0.95 + random.gauss(0, 0.02)
        power_factor = max(0.85, min(1.0, power_factor))
        
        power = voltage * current * power_factor  # Watts
        
        # Energy consumed in this reading (assuming 1-minute intervals)
        energy_consumed = (power / 1000) / 60  # kWh per minute
        self.total_energy_consumed += energy_consumed
        
        # Frequency (typically 50 or 60 Hz)
        frequency = 50.0 + random.gauss(0, 0.1)
        
        # Determine consumption level
        consumption_level = self._classify_consumption(power)
        
        # Create reading
        reading = EnergyReading(
            meter_id=self.meter_id,
            timestamp=timestamp,
            voltage=voltage,
            current=current,
            power=power,
            energy_consumed=energy_consumed,
            frequency=frequency,
            power_factor=power_factor,
            consumption_level=consumption_level
        )
        
        self.readings.append(reading)
        self.last_reading = reading
        
        # Check for anomalies
        self._detect_anomalies(reading)
        
        return reading
    
    def _generate_current(self, hour_of_day: int, day_type: str) -> float:
        """Generate realistic current draw based on time and day type"""
        base_current = 0.5  # Amperes
        
        if day_type == "holiday":
            # Lower consumption on holidays
            if 6 <= hour_of_day < 9:
                current = random.uniform(2, 4)
            elif 9 <= hour_of_day < 17:
                current = random.uniform(1, 2)
            elif 17 <= hour_of_day < 22:
                current = random.uniform(3, 6)
            else:
                current = random.uniform(0.5, 1.5)
        elif day_type == "weekend":
            if 6 <= hour_of_day < 9:
                current = random.uniform(3, 5)
            elif 9 <= hour_of_day < 17:
                current = random.uniform(2, 4)
            elif 17 <= hour_of_day < 23:
                current = random.uniform(4, 7)
            else:
                current = random.uniform(1, 2)
        else:  # Weekday
            if 6 <= hour_of_day < 9:
                current = random.uniform(2, 3)
            elif 9 <= hour_of_day < 17:
                current = random.uniform(1, 2)
            elif 17 <= hour_of_day < 22:
                current = random.uniform(5, 10)
            else:
                current = random.uniform(0.5, 1.5)
        
        # Add random noise
        current += random.gauss(0, 0.2)
        return max(0, current)
    
    def _classify_consumption(self, power: float) -> ConsumptionLevel:
        """Classify power consumption into levels"""
        if power < 500:
            return ConsumptionLevel.VERY_LOW
        elif power < 1000:
            return ConsumptionLevel.LOW
        elif power < 2000:
            return ConsumptionLevel.MODERATE
        elif power < 3500:
            return ConsumptionLevel.HIGH
        else:
            return ConsumptionLevel.VERY_HIGH
    
    def _detect_anomalies(self, reading: EnergyReading):
        """Detect anomalies in consumption patterns"""
        if len(self.readings) < 2:
            return
        
        prev_reading = self.readings[-2]
        
        # Check for sudden spikes
        power_change = abs(reading.power - prev_reading.power)
        if power_change > 2000:
            alert = EnergyAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                meter_id=self.meter_id,
                alert_type="ANOMALY",
                severity="WARNING",
                message=f"Sudden power spike detected: {prev_reading.power:.0f}W -> {reading.power:.0f}W",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
            logger.warning(f"Anomaly detected in meter {self.meter_id}: {alert.message}")
        
        # Check for sustained high consumption
        if reading.power > 3500 and len(self.readings) > 10:
            recent_readings = [r.power for r in self.readings[-10:]]
            if all(p > 3000 for p in recent_readings):
                alert = EnergyAlert(
                    alert_id=f"ALERT_{len(self.alerts) + 1}",
                    meter_id=self.meter_id,
                    alert_type="HIGH_CONSUMPTION",
                    severity="WARNING",
                    message=f"Sustained high consumption detected: Average {sum(recent_readings)/len(recent_readings):.0f}W",
                    timestamp=datetime.datetime.now()
                )
                self.alerts.append(alert)
        
        # Check for voltage issues
        if reading.voltage < 200 or reading.voltage > 240:
            alert = EnergyAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                meter_id=self.meter_id,
                alert_type="VOLTAGE_ISSUE",
                severity="CRITICAL",
                message=f"Voltage out of range: {reading.voltage:.1f}V",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
    
    def calculate_bill(self, period_start: datetime.datetime, period_end: datetime.datetime, 
                      rate_per_kwh: float = 5.0) -> BillingRecord:
        """
        Calculate billing for a period
        
        Args:
            period_start: Start of billing period
            period_end: End of billing period
            rate_per_kwh: Rate per kWh in currency units
            
        Returns:
            BillingRecord object
        """
        # Filter readings for the period
        period_readings = [r for r in self.readings 
                          if period_start <= r.timestamp <= period_end]
        
        total_energy = sum(r.energy_consumed for r in period_readings)
        
        # Differentiate between peak and off-peak hours
        peak_hours = []
        off_peak_hours = []
        
        for reading in period_readings:
            hour = reading.timestamp.hour
            if 9 <= hour < 21:  # Peak hours
                peak_hours.append(reading.energy_consumed)
            else:
                off_peak_hours.append(reading.energy_consumed)
        
        peak_energy = sum(peak_hours)
        off_peak_energy = sum(off_peak_hours)
        
        # Apply differential rates
        peak_rate = rate_per_kwh * 1.2  # 20% premium for peak hours
        off_peak_rate = rate_per_kwh * 0.8  # 20% discount for off-peak
        
        total_amount = (peak_energy * peak_rate) + (off_peak_energy * off_peak_rate)
        
        billing = BillingRecord(
            meter_id=self.meter_id,
            period_start=period_start,
            period_end=period_end,
            total_energy_kwh=total_energy,
            rate_per_kwh=rate_per_kwh,
            total_amount=total_amount,
            peak_hour_units=peak_energy,
            off_peak_units=off_peak_energy
        )
        
        return billing
    
    def get_meter_status(self) -> Dict:
        """Get current meter status"""
        return {
            'meter_id': self.meter_id,
            'location': self.location,
            'meter_type': self.meter_type,
            'status': self.status.value,
            'total_energy_consumed_kwh': round(self.total_energy_consumed, 2),
            'last_reading': self.last_reading.to_dict() if self.last_reading else None,
            'total_readings': len(self.readings),
            'active_alerts': len([a for a in self.alerts if not a.resolved]),
            'firmware_version': self.firmware_version
        }


class EnergyMonitoringNetwork:
    """Network of smart energy meters"""
    
    def __init__(self, network_name: str, num_meters: int):
        """
        Initialize an energy monitoring network
        
        Args:
            network_name: Name of the network
            num_meters: Number of meters in the network
        """
        self.network_name = network_name
        self.num_meters = num_meters
        self.meters: Dict[str, SmartEnergyMeter] = {}
        self.network_alerts: List[EnergyAlert] = []
        self.operation_log: List[Dict] = []
        
        self._initialize_meters()
        logger.info(f"Energy monitoring network '{network_name}' initialized with {num_meters} meters")
    
    def _initialize_meters(self):
        """Initialize all meters"""
        meter_types = ["Residential", "Commercial", "Industrial"]
        
        for i in range(self.num_meters):
            meter_id = f"EM_{i+1:05d}"
            meter_type = meter_types[i % len(meter_types)]
            location = f"Building {i//10 + 1}, Unit {i%10 + 1}"
            
            meter = SmartEnergyMeter(meter_id, location, meter_type)
            self.meters[meter_id] = meter
    
    def read_all_meters(self, hour_of_day: int = 12, day_type: str = "weekday"):
        """Read all meters in the network"""
        for meter_id, meter in self.meters.items():
            reading = meter.take_reading(hour_of_day, day_type)
            
            # Collect alerts
            for alert in meter.alerts:
                if not alert.resolved:
                    self.network_alerts.append(alert)
    
    def get_network_statistics(self) -> Dict:
        """Get network-wide statistics"""
        total_meters = len(self.meters)
        active_meters = sum(1 for m in self.meters.values() if m.status == MeterStatus.ACTIVE)
        faulty_meters = sum(1 for m in self.meters.values() if m.status == MeterStatus.FAULTY)
        
        total_power = sum(m.last_reading.power for m in self.meters.values() 
                         if m.last_reading is not None)
        
        total_energy = sum(m.total_energy_consumed for m in self.meters.values())
        
        # Consumption distribution
        consumption_dist = {}
        for level in ConsumptionLevel:
            count = sum(1 for m in self.meters.values() 
                       if m.last_reading and m.last_reading.consumption_level == level)
            consumption_dist[level.value] = count
        
        return {
            'total_meters': total_meters,
            'active_meters': active_meters,
            'faulty_meters': faulty_meters,
            'total_power_consumption_kw': round(total_power / 1000, 2),
            'total_energy_consumed_kwh': round(total_energy, 2),
            'consumption_distribution': consumption_dist,
            'active_alerts': len([a for a in self.network_alerts if not a.resolved]),
            'network_health_percentage': round((active_meters / total_meters) * 100, 2)
        }
    
    def get_hourly_report(self) -> Dict:
        """Generate hourly monitoring report"""
        stats = self.get_network_statistics()
        
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'network_name': self.network_name,
            'statistics': stats,
            'estimated_daily_cost': self._estimate_daily_cost()
        }
        
        self.operation_log.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'total_power_kw': stats['total_power_consumption_kw'],
            'active_meters': stats['active_meters'],
            'faulty_meters': stats['faulty_meters']
        })
        
        return report
    
    def _estimate_daily_cost(self, rate_per_kwh: float = 5.0) -> float:
        """Estimate daily electricity cost"""
        stats = self.get_network_statistics()
        # Assuming 24 hours of similar consumption
        estimated_daily_energy = stats['total_energy_consumed_kwh'] * 24
        return round(estimated_daily_energy * rate_per_kwh, 2)
    
    def export_to_json(self, filename: str):
        """Export network data to JSON"""
        data = {
            'network_name': self.network_name,
            'total_meters': self.num_meters,
            'meters': {meter_id: meter.get_meter_status() for meter_id, meter in self.meters.items()},
            'network_alerts': [alert.to_dict() for alert in self.network_alerts],
            'operation_log': self.operation_log
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to {filename}")


class EnergySimulator:
    """Simulator for generating realistic energy consumption scenarios"""
    
    def __init__(self, network: EnergyMonitoringNetwork):
        """Initialize simulator"""
        self.network = network
    
    def simulate_24_hour_cycle(self):
        """Simulate a full 24-hour consumption cycle"""
        logger.info("Starting 24-hour energy consumption simulation")
        
        for hour in range(24):
            # Determine day type (for demo, assume weekday)
            day_type = "weekday"
            
            # Read all meters
            self.network.read_all_meters(hour_of_day=hour, day_type=day_type)
            
            # Generate hourly report
            report = self.network.get_hourly_report()
            
            logger.info(f"Hour {hour:02d}:00 - Power: {report['statistics']['total_power_consumption_kw']}kW, "
                       f"Meters: Active={report['statistics']['active_meters']}, "
                       f"Faulty={report['statistics']['faulty_meters']}")
        
        logger.info("24-hour simulation completed")
    
    def get_simulation_report(self) -> Dict:
        """Get comprehensive simulation report"""
        return self.network.get_hourly_report()


if __name__ == "__main__":
    # Create energy monitoring network
    network = EnergyMonitoringNetwork(
        network_name="Smart City District A",
        num_meters=100
    )
    
    # Create simulator
    simulator = EnergySimulator(network)
    
    # Run simulation
    simulator.simulate_24_hour_cycle()
    
    # Generate report
    report = simulator.get_simulation_report()
    
    # Print report
    print("\n" + "="*60)
    print("SMART ENERGY METERING SYSTEM - SIMULATION REPORT")
    print("="*60)
    print(json.dumps(report, indent=2))
    
    # Export data
    network.export_to_json('/home/ubuntu/energy_metering_data.json')
