"""
Management command to seed the database with sample solar products.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush   (clear existing data first)
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Category, Product


CATEGORIES = [
    {'name': 'Solar Panels', 'description': 'High-efficiency monocrystalline and polycrystalline solar panels.'},
    {'name': 'Inverters', 'description': 'String inverters, micro-inverters, and hybrid inverters.'},
    {'name': 'Batteries', 'description': 'Lithium-ion and lead-acid solar storage batteries.'},
    {'name': 'Charge Controllers', 'description': 'MPPT and PWM charge controllers for solar systems.'},
    {'name': 'Mounting Structures', 'description': 'Rooftop and ground-mount racking systems.'},
    {'name': 'Accessories', 'description': 'Cables, connectors, junction boxes, and tools.'},
]

PRODUCTS = [
    # Solar Panels
    {'category': 'Solar Panels', 'name': 'SolarMax 540W Mono PERC Panel', 'sku': 'SP-540-MONO', 'price': '18500.00', 'discount_percent': '10', 'capacity': '540W', 'warranty_years': 25, 'lifespan_years': 30, 'stock': 150, 'delivery_days': 5, 'installation_fee': '2500.00', 'description': 'Tier-1 monocrystalline PERC panel with 21.3% efficiency. Ideal for residential and commercial rooftops.', 'technical_description': 'Cell Type: Mono PERC | Vmp: 41.2V | Imp: 13.11A | Dimensions: 2278×1134×35mm | Weight: 28.5kg | IP68 Junction Box'},
    {'category': 'Solar Panels', 'name': 'EcoSun 440W Poly Panel', 'sku': 'SP-440-POLY', 'price': '13200.00', 'discount_percent': '5', 'capacity': '440W', 'warranty_years': 20, 'lifespan_years': 25, 'stock': 200, 'delivery_days': 5, 'installation_fee': '2000.00', 'description': 'Budget-friendly polycrystalline panel for large-scale installations.'},
    {'category': 'Solar Panels', 'name': 'UltraVolt 600W Bifacial Panel', 'sku': 'SP-600-BIFI', 'price': '24000.00', 'discount_percent': '8', 'capacity': '600W', 'warranty_years': 30, 'lifespan_years': 35, 'stock': 80, 'delivery_days': 7, 'installation_fee': '3000.00', 'description': 'Premium bifacial panel with up to 30% extra yield from rear-side generation.'},

    # Inverters
    {'category': 'Inverters', 'name': 'PowerGrid 5kW Hybrid Inverter', 'sku': 'INV-5KW-HYB', 'price': '45000.00', 'discount_percent': '12', 'capacity': '5kW', 'warranty_years': 10, 'lifespan_years': 15, 'stock': 60, 'delivery_days': 7, 'installation_fee': '5000.00', 'description': 'Hybrid inverter with built-in MPPT charger. Supports on-grid and off-grid modes.'},
    {'category': 'Inverters', 'name': 'MicroSun 800W Micro-Inverter', 'sku': 'INV-800-MIC', 'price': '8500.00', 'discount_percent': '0', 'capacity': '800W', 'warranty_years': 15, 'lifespan_years': 20, 'stock': 300, 'delivery_days': 3, 'installation_fee': '1500.00', 'description': 'Panel-level micro-inverter for maximum energy harvest and monitoring.'},
    {'category': 'Inverters', 'name': 'SunForce 10kW String Inverter', 'sku': 'INV-10KW-STR', 'price': '72000.00', 'discount_percent': '15', 'capacity': '10kW', 'warranty_years': 10, 'lifespan_years': 15, 'stock': 40, 'delivery_days': 10, 'installation_fee': '7000.00', 'description': 'High-power string inverter for commercial rooftops. Dual MPPT tracking.'},

    # Batteries
    {'category': 'Batteries', 'name': 'LithStore 5kWh LiFePO4 Battery', 'sku': 'BAT-5KWH-LFP', 'price': '95000.00', 'discount_percent': '5', 'capacity': '5kWh', 'warranty_years': 10, 'lifespan_years': 15, 'stock': 50, 'delivery_days': 7, 'installation_fee': '4000.00', 'description': 'Long-cycle lithium iron phosphate battery. 6000+ cycles at 80% DoD.'},
    {'category': 'Batteries', 'name': 'PowerWall 10kWh Home Battery', 'sku': 'BAT-10KWH-LI', 'price': '175000.00', 'discount_percent': '10', 'capacity': '10kWh', 'warranty_years': 12, 'lifespan_years': 18, 'stock': 30, 'delivery_days': 10, 'installation_fee': '8000.00', 'description': 'Whole-home backup battery with integrated BMS and smart monitoring.'},
    {'category': 'Batteries', 'name': 'EcoBatt 150Ah Tubular Battery', 'sku': 'BAT-150AH-TUB', 'price': '14500.00', 'discount_percent': '0', 'capacity': '150Ah', 'warranty_years': 5, 'lifespan_years': 8, 'stock': 120, 'delivery_days': 4, 'installation_fee': '1500.00', 'description': 'Reliable lead-acid tubular battery for budget solar setups.'},

    # Charge Controllers
    {'category': 'Charge Controllers', 'name': 'MPPT Pro 60A Controller', 'sku': 'CC-60A-MPPT', 'price': '12000.00', 'discount_percent': '8', 'capacity': '60A', 'warranty_years': 5, 'lifespan_years': 10, 'stock': 100, 'delivery_days': 3, 'installation_fee': '1000.00', 'description': '60A MPPT charge controller with LCD display. 99% tracking efficiency.'},
    {'category': 'Charge Controllers', 'name': 'PWM Basic 30A Controller', 'sku': 'CC-30A-PWM', 'price': '2200.00', 'discount_percent': '0', 'capacity': '30A', 'warranty_years': 2, 'lifespan_years': 5, 'stock': 250, 'delivery_days': 2, 'installation_fee': '500.00', 'description': 'Entry-level PWM controller for small off-grid systems.'},

    # Mounting Structures
    {'category': 'Mounting Structures', 'name': 'RoofRack Aluminium Mount (4-panel)', 'sku': 'MNT-ALU-4P', 'price': '6500.00', 'discount_percent': '5', 'capacity': '4 panels', 'warranty_years': 15, 'lifespan_years': 25, 'stock': 80, 'delivery_days': 5, 'installation_fee': '3500.00', 'description': 'Corrosion-resistant aluminium rooftop mounting kit for 4 panels.'},
    {'category': 'Mounting Structures', 'name': 'GroundFrame GI Mount (8-panel)', 'sku': 'MNT-GI-8P', 'price': '14000.00', 'discount_percent': '10', 'capacity': '8 panels', 'warranty_years': 20, 'lifespan_years': 30, 'stock': 40, 'delivery_days': 8, 'installation_fee': '6000.00', 'description': 'Hot-dip galvanised ground-mount structure for 8 panels with tilt adjustment.'},

    # Accessories
    {'category': 'Accessories', 'name': 'Solar DC Cable 4mm² (100m)', 'sku': 'ACC-CABLE-4MM', 'price': '3500.00', 'discount_percent': '0', 'capacity': '100m', 'warranty_years': 5, 'lifespan_years': 15, 'stock': 500, 'delivery_days': 2, 'installation_fee': '0.00', 'description': 'UV-resistant double-insulated DC cable rated for 1500V.', 'installation_available': False},
    {'category': 'Accessories', 'name': 'MC4 Connector Pair (10 sets)', 'sku': 'ACC-MC4-10', 'price': '850.00', 'discount_percent': '0', 'capacity': '10 pairs', 'warranty_years': 10, 'lifespan_years': 20, 'stock': 600, 'delivery_days': 2, 'installation_fee': '0.00', 'description': 'IP67 waterproof MC4 connectors for panel-to-cable connections.', 'installation_available': False},
]


class Command(BaseCommand):
    help = 'Seed the database with sample solar products and categories.'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing products/categories first.')

    def handle(self, *args, **options):
        if options['flush']:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('Flushed existing products & categories.'))

        # Create categories
        cat_map = {}
        for cat_data in CATEGORIES:
            obj, created = Category.objects.get_or_create(
                slug=slugify(cat_data['name']),
                defaults={**cat_data, 'slug': slugify(cat_data['name'])},
            )
            cat_map[cat_data['name']] = obj
            status_msg = 'created' if created else 'exists'
            self.stdout.write(f'  Category: {obj.name} [{status_msg}]')

        # Create products
        created_count = 0
        for prod_data in PRODUCTS:
            category = cat_map[prod_data.pop('category')]
            slug = slugify(prod_data['name'])
            installation_available = prod_data.pop('installation_available', True)

            _, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    **prod_data,
                    'slug': slug,
                    'category': category,
                    'price': Decimal(prod_data['price']),
                    'discount_percent': Decimal(prod_data.get('discount_percent', '0')),
                    'installation_fee': Decimal(prod_data.get('installation_fee', '0')),
                    'installation_available': installation_available,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {created_count} products seeded across {len(cat_map)} categories.'
        ))
