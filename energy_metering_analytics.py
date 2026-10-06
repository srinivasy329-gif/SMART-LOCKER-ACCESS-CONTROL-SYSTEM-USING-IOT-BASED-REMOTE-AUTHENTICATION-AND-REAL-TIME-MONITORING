"""
Smart Energy Metering Analytics and Visualization Module

This module provides comprehensive analytics, reporting, and visualization capabilities
for the Smart Energy Metering and Monitoring System.

Author: Internship Project Team
Date: 2024
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta
import random
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class EnergyAnalytics:
    """Analytics class for energy metering system data"""
    
    def __init__(self, network):
        """Initialize analytics with network data"""
        self.network = network
        self.data = None
    
    def load_data(self, json_file: str = None):
        """Load energy metering data from JSON file"""
        if json_file:
            with open(json_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'network_name': self.network.network_name,
                'total_meters': self.network.num_meters,
                'meters': {meter_id: meter.get_meter_status() for meter_id, meter in self.network.meters.items()},
                'network_alerts': [alert.to_dict() for alert in self.network.network_alerts],
                'operation_log': self.network.operation_log
            }
    
    def generate_consumption_pattern_chart(self, output_file: str = '/home/ubuntu/consumption_pattern.png'):
        """Generate 24-hour consumption pattern chart"""
        hours = np.arange(0, 24, 1)
        consumption = []
        
        for hour in hours:
            if 6 <= hour < 9:  # Morning peak
                cons = random.uniform(80, 100)
            elif 9 <= hour < 17:  # Daytime moderate
                cons = random.uniform(40, 60)
            elif 17 <= hour < 22:  # Evening peak
                cons = random.uniform(90, 110)
            else:  # Night low
                cons = random.uniform(20, 40)
            
            consumption.append(cons)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Consumption line chart
        ax1.plot(hours, consumption, marker='o', linewidth=3, markersize=8,
                color='#FF6B6B', label='Total Consumption (kW)')
        ax1.fill_between(hours, consumption, alpha=0.3, color='#FF6B6B')
        
        # Add peak threshold
        ax1.axhline(y=100, color='#FFD93D', linestyle='--', linewidth=2, label='Peak Threshold', alpha=0.7)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Consumption (kW)', fontsize=12, fontweight='bold')
        ax1.set_title('24-Hour Energy Consumption Pattern', fontsize=14, fontweight='bold')
        ax1.set_xticks(hours)
        ax1.set_xticklabels([f'{int(h):02d}:00' for h in hours], rotation=45)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Weekly comparison
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_consumption = [random.uniform(800, 1200) for _ in days]
        
        colors = ['#FF6B6B' if c > 1100 else '#FFD93D' if c > 900 else '#4ECDC4' for c in daily_consumption]
        bars = ax2.bar(days, daily_consumption, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax2.set_ylabel('Daily Consumption (kWh)', fontsize=12, fontweight='bold')
        ax2.set_title('Weekly Energy Consumption Comparison', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, consumption_val in zip(bars, daily_consumption):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{consumption_val:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Consumption pattern chart saved to {output_file}")
        plt.close()
    
    def generate_cost_analysis_chart(self, output_file: str = '/home/ubuntu/cost_analysis.png'):
        """Generate electricity cost analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Monthly cost breakdown
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_costs = [random.uniform(3000, 5000) for _ in months]
        
        ax1.plot(months, monthly_costs, marker='s', linewidth=3, markersize=8,
                color='#45B7D1', label='Monthly Cost')
        ax1.fill_between(range(len(months)), monthly_costs, alpha=0.3, color='#45B7D1')
        
        # Add average line
        avg_cost = sum(monthly_costs) / len(monthly_costs)
        ax1.axhline(y=avg_cost, color='#FFD93D', linestyle='--', linewidth=2, label=f'Average: ₹{avg_cost:.0f}')
        
        ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Cost (₹)', fontsize=12, fontweight='bold')
        ax1.set_title('Annual Electricity Cost Trend', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Peak vs Off-Peak cost breakdown
        categories = ['Peak Hours\n(9 AM - 9 PM)', 'Off-Peak Hours\n(9 PM - 9 AM)']
        costs = [random.uniform(2000, 3500), random.uniform(800, 1500)]
        
        colors_peak = ['#FF6B6B', '#4ECDC4']
        bars = ax2.bar(categories, costs, color=colors_peak, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax2.set_ylabel('Monthly Cost (₹)', fontsize=12, fontweight='bold')
        ax2.set_title('Peak vs Off-Peak Cost Distribution', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'₹{cost:.0f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Cost analysis chart saved to {output_file}")
        plt.close()
    
    def generate_meter_health_dashboard(self, output_file: str = '/home/ubuntu/meter_health.png'):
        """Generate meter health and status dashboard"""
        stats = self.network.get_network_statistics()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Meter status pie chart
        status_data = {
            'Active': stats['active_meters'],
            'Faulty': stats['faulty_meters'],
            'Inactive': self.network.num_meters - stats['active_meters'] - stats['faulty_meters']
        }
        
        colors = ['#4ECDC4', '#FF6B6B', '#FFD93D']
        explode = (0.05, 0.1, 0)
        wedges, texts, autotexts = ax1.pie(status_data.values(), labels=status_data.keys(),
                                            autopct='%1.1f%%', colors=colors, explode=explode,
                                            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Meter Status Distribution', fontsize=14, fontweight='bold')
        
        # Consumption level distribution
        consumption_dist = stats['consumption_distribution']
        levels = list(consumption_dist.keys())
        counts = list(consumption_dist.values())
        
        colors_cons = ['#4ECDC4', '#A8E6CF', '#FFD93D', '#FF8C42', '#FF6B6B']
        bars = ax2.bar(levels, counts, color=colors_cons, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax2.set_ylabel('Number of Meters', fontsize=12, fontweight='bold')
        ax2.set_title('Consumption Level Distribution', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add count labels
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Meter health dashboard saved to {output_file}")
        plt.close()
    
    def generate_voltage_analysis(self, output_file: str = '/home/ubuntu/voltage_analysis.png'):
        """Generate voltage and power quality analysis"""
        hours = np.arange(0, 24, 1)
        voltages = [230 + random.gauss(0, 2) for _ in hours]
        power_factors = [0.95 + random.gauss(0, 0.02) for _ in hours]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Voltage variation
        ax1.plot(hours, voltages, marker='o', linewidth=2.5, markersize=7, color='#45B7D1')
        ax1.fill_between(hours, 200, 240, alpha=0.1, color='green', label='Safe Range')
        ax1.axhline(y=230, color='#FFD93D', linestyle='--', linewidth=2, label='Nominal (230V)', alpha=0.7)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Voltage (V)', fontsize=12, fontweight='bold')
        ax1.set_title('24-Hour Voltage Variation', fontsize=14, fontweight='bold')
        ax1.set_xticks(hours[::2])
        ax1.set_xticklabels([f'{int(h):02d}:00' for h in hours[::2]], rotation=45)
        ax1.set_ylim(190, 250)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Power factor trend
        ax2.plot(hours, power_factors, marker='s', linewidth=2.5, markersize=7, color='#FF6B6B')
        ax2.axhline(y=0.95, color='#4ECDC4', linestyle='--', linewidth=2, label='Target (0.95)', alpha=0.7)
        ax2.fill_between(hours, 0.85, 1.0, alpha=0.1, color='green', label='Acceptable Range')
        
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Power Factor', fontsize=12, fontweight='bold')
        ax2.set_title('24-Hour Power Factor Trend', fontsize=14, fontweight='bold')
        ax2.set_xticks(hours[::2])
        ax2.set_xticklabels([f'{int(h):02d}:00' for h in hours[::2]], rotation=45)
        ax2.set_ylim(0.8, 1.05)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Voltage analysis chart saved to {output_file}")
        plt.close()
    
    def generate_alert_summary(self, output_file: str = '/home/ubuntu/alert_summary.png'):
        """Generate alert and anomaly summary"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Alert types distribution
        alert_types = {
            'Anomaly': random.randint(5, 15),
            'High Consumption': random.randint(3, 10),
            'Voltage Issue': random.randint(2, 8),
            'Fault': random.randint(1, 5),
            'Normal': self.network.num_meters - random.randint(15, 35)
        }
        
        colors_alerts = ['#FF6B6B', '#FF8C42', '#FFD93D', '#A0A0A0', '#4ECDC4']
        wedges, texts, autotexts = ax1.pie(alert_types.values(), labels=alert_types.keys(),
                                            autopct='%1.1f%%', colors=colors_alerts, startangle=90,
                                            textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax1.set_title('Alert Type Distribution', fontsize=14, fontweight='bold')
        
        # Hourly alert count
        hours = np.arange(0, 24, 1)
        alert_counts = [random.randint(0, 5) for _ in hours]
        
        ax2.bar(hours, alert_counts, color='#FF6B6B', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Alerts', fontsize=12, fontweight='bold')
        ax2.set_title('Hourly Alert Distribution', fontsize=14, fontweight='bold')
        ax2.set_xticks(hours[::2])
        ax2.set_xticklabels([f'{int(h):02d}:00' for h in hours[::2]], rotation=45)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Alert summary chart saved to {output_file}")
        plt.close()
    
    def generate_efficiency_metrics(self, output_file: str = '/home/ubuntu/efficiency_metrics.png'):
        """Generate efficiency metrics dashboard"""
        stats = self.network.get_network_statistics()
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        
        # KPI boxes
        kpis = [
            ('Total Meters', stats['total_meters'], '#2E86AB'),
            ('Active Meters', stats['active_meters'], '#4ECDC4'),
            ('Faulty Meters', stats['faulty_meters'], '#FF6B6B'),
            ('Power (kW)', f"{stats['total_power_consumption_kw']:.2f}", '#45B7D1'),
            ('Energy (kWh)', f"{stats['total_energy_consumed_kwh']:.2f}", '#A8E6CF'),
            ('Network Health', f"{stats['network_health_percentage']:.1f}%", '#FFD93D'),
        ]
        
        for idx, (title, value, color) in enumerate(kpis):
            ax = fig.add_subplot(gs[idx // 3, idx % 3])
            ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.2), 0.9, 0.6,
                                                boxstyle="round,pad=0.05", 
                                                edgecolor=color, facecolor=color, alpha=0.2, linewidth=2))
            ax.text(0.5, 0.65, title, ha='center', va='center', fontsize=12, fontweight='bold')
            ax.text(0.5, 0.35, str(value), ha='center', va='center', fontsize=24, fontweight='bold', color=color)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Summary text
        ax_summary = fig.add_subplot(gs[2, :])
        summary_text = f"""
        ENERGY MONITORING NETWORK: {self.network.network_name} | TOTAL METERS: {stats['total_meters']}
        
        Current Status: {stats['active_meters']} active | {stats['faulty_meters']} faulty | Network Health: {stats['network_health_percentage']:.1f}%
        
        Power Consumption: {stats['total_power_consumption_kw']:.2f} kW | Total Energy: {stats['total_energy_consumed_kwh']:.2f} kWh | Active Alerts: {stats['active_alerts']}
        """
        ax_summary.text(0.05, 0.5, summary_text, fontsize=11, verticalalignment='center',
                       family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax_summary.axis('off')
        
        fig.suptitle('Smart Energy Metering System - Efficiency Metrics Dashboard', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Efficiency metrics dashboard saved to {output_file}")
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualization charts"""
        logger.info("Generating all visualization charts...")
        self.generate_consumption_pattern_chart()
        self.generate_cost_analysis_chart()
        self.generate_meter_health_dashboard()
        self.generate_voltage_analysis()
        self.generate_alert_summary()
        self.generate_efficiency_metrics()
        logger.info("All visualizations generated successfully!")


if __name__ == "__main__":
    from smart_energy_metering_system import EnergyMonitoringNetwork, EnergySimulator
    
    # Create network
    network = EnergyMonitoringNetwork(
        network_name="Smart City District A",
        num_meters=100
    )
    
    # Run simulation
    simulator = EnergySimulator(network)
    simulator.simulate_24_hour_cycle()
    
    # Generate analytics
    analytics = EnergyAnalytics(network)
    analytics.generate_all_visualizations()
    
    print("Analytics generation completed!")
