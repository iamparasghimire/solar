from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Seed the database with sample categories and products for local testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')

        categories = [
            'Panels', 'Inverters', 'Batteries', 'Controllers',
            'Mounting', 'Accessories', 'Monitoring', 'Heating'
        ]

        cat_objs = {}
        for name in categories:
            obj, created = Category.objects.get_or_create(
                slug=slugify(name), defaults={'name': name}
            )
            cat_objs[name] = obj
            if created:
                self.stdout.write(f'  Created category: {name}')

        sample_products = [
            {
                'name': 'SunPower Ultra 540W Panel',
                'category': 'Panels',
                'sku': 'SP-540-001',
                'price': '349.99',
                'discount_percent': '5',
                'capacity': '540W',
                'warranty_years': 25,
                'lifespan_years': 30,
                'stock': 50,
                'installation_fee': '120.00',
                'brand': 'SunPower',
            },
            {
                'name': 'EcoInvert 5kW Inverter',
                'category': 'Inverters',
                'sku': 'EI-5000-INV',
                'price': '899.00',
                'discount_percent': '10',
                'capacity': '5kW',
                'warranty_years': 10,
                'lifespan_years': 15,
                'stock': 20,
                'installation_fee': '200.00',
                'brand': 'EcoInvert',
            },
            {
                'name': 'PowerVault 10kWh Battery',
                'category': 'Batteries',
                'sku': 'PV-10K-BAT',
                'price': '4999.00',
                'discount_percent': '8',
                'capacity': '10kWh',
                'warranty_years': 10,
                'lifespan_years': 15,
                'stock': 10,
                'installation_fee': '500.00',
                'brand': 'PowerVault',
            },
            {
                'name': 'SmartCharge MPPT Controller',
                'category': 'Controllers',
                'sku': 'SC-MPPT-1',
                'price': '149.99',
                'discount_percent': '0',
                'capacity': '60A',
                'warranty_years': 5,
                'lifespan_years': 8,
                'stock': 100,
                'installation_fee': '0.00',
                'brand': 'SmartCharge',
            },
            {
                'name': 'RoofMount Aluminum Kit',
                'category': 'Mounting',
                'sku': 'RM-ALU-01',
                'price': '299.00',
                'discount_percent': '0',
                'capacity': '',
                'warranty_years': 10,
                'lifespan_years': 25,
                'stock': 200,
                'installation_fee': '0.00',
                'brand': 'MountPro',
            },
            {
                'name': 'Connector & Cable Pack',
                'category': 'Accessories',
                'sku': 'ACC-CBL-01',
                'price': '39.99',
                'discount_percent': '0',
                'capacity': '',
                'warranty_years': 1,
                'lifespan_years': 5,
                'stock': 500,
                'installation_fee': '0.00',
                'brand': 'SolarLink',
            },
            {
                'name': 'SolarMonitor Pro',
                'category': 'Monitoring',
                'sku': 'SM-PRO-01',
                'price': '199.00',
                'discount_percent': '15',
                'capacity': '',
                'warranty_years': 3,
                'lifespan_years': 7,
                'stock': 150,
                'installation_fee': '0.00',
                'brand': 'SolarSense',
            },
            {
                'name': 'SolarWater Heater 200L',
                'category': 'Heating',
                'sku': 'HW-200-01',
                'price': '799.00',
                'discount_percent': '12',
                'capacity': '200L',
                'warranty_years': 5,
                'lifespan_years': 12,
                'stock': 30,
                'installation_fee': '150.00',
                'brand': 'HeatSolar',
            },
        ]

        self.stdout.write('Seeding products...')
        created_count = 0
        for p in sample_products:
            cat = cat_objs.get(p['category'])
            slug = slugify(p['name'])
            obj, created = Product.objects.get_or_create(
                sku=p['sku'],
                defaults={
                    'category': cat,
                    'name': p['name'],
                    'slug': slug,
                    'description': '',
                    'technical_description': '',
                    'price': Decimal(p['price']),
                    'discount_percent': Decimal(p['discount_percent']),
                    'capacity': p.get('capacity', ''),
                    'warranty_years': p.get('warranty_years', 0),
                    'lifespan_years': p.get('lifespan_years', 0),
                    'stock': p.get('stock', 0),
                    'installation_fee': Decimal(p.get('installation_fee', '0.00')),
                    'brand': p.get('brand', ''),
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f"  Created product: {obj.name} ({obj.sku})")

        self.stdout.write(self.style.SUCCESS(f'Seeding complete — {created_count} products created'))
