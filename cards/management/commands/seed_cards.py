from django.core.management.base import BaseCommand
from django.utils.text import slugify
from cards.models import Category, WeddingCard


CATEGORIES = [
    ('Hindu',        'hindu'),
    ('South Indian', 'south-indian'),
    ('Muslim',       'muslim'),
    ('Christian',    'christian'),
    ('Marathi',      'marathi'),
    ('Bengali',      'bengali'),
    ('Sikh',         'sikh'),
    ('Rajasthani',   'rajasthani'),
    ('Generic',      'generic'),
]

SAMPLE_CARDS = [
    # (name, cat_slug, palette, ornament, price, featured)
    ('Sacred Ganesh',       'hindu',        'gold',      '🕉',  1499, True),
    ('Vedic Bloom',         'hindu',        'floral',    '❦',   1299, True),
    ('Kolam Elegance',      'south-indian', 'botanical', '🌸',  1599, True),
    ('Temple Gold',         'south-indian', 'gold',      '⚜',  1799, True),
    ('Crescent & Stars',    'muslim',       'classic',   '✦',  1399, True),
    ('Nikah Invitation',    'muslim',       'minimal',   '✿',  1199, False),
    ('Cross & Roses',       'christian',    'minimal',   '✝',  1299, False),
    ('Divine Grace',        'christian',    'floral',    '🌹',  1099, False),
    ('Warli Art',           'marathi',      'rustic',    '🌾',  1199, False),
    ('Puneri Classic',      'marathi',      'gold',      '⚜',  1499, False),
    ('Alpona Design',       'bengali',      'botanical', '🌺',  1399, False),
    ('Durga Blessing',      'bengali',      'floral',    '❦',   1299, False),
    ('Ik Onkar',            'sikh',         'gold',      '☬',  1599, False),
    ('Anand Karaj',         'sikh',         'minimal',   '✦',  1399, False),
    ('Rajputana Royale',    'rajasthani',   'rustic',    '🏰',  1999, True),
    ('Jaipuri Miniature',   'rajasthani',   'gold',      '⚜',  1799, True),
    ('Simple Elegance',     'generic',      'minimal',   '✦',   999, False),
    ('Classic Gold',        'generic',      'gold',      '❦',  1299, False),
]


class Command(BaseCommand):
    help = 'Seed correct categories and sample wedding cards'

    def handle(self, *args, **kwargs):
        # 1. Remove old incorrect categories
        old_slugs = ['floral', 'minimal', 'luxury', 'classic', 'rustic', 'botanical']
        deleted = Category.objects.filter(slug__in=old_slugs).delete()
        self.stdout.write(f'Removed old categories: {deleted}')

        # 2. Create correct categories
        cats = {}
        for name, slug in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=slug, defaults={'name': name}
            )
            cats[slug] = cat
            status = 'created' if created else 'exists'
            self.stdout.write(f'  ✔ {name} ({status})')

        self.stdout.write(self.style.SUCCESS(f'✔ {len(CATEGORIES)} categories ready'))

        # 3. Seed sample cards
        count = 0
        for name, cat_slug, palette, ornament, price, featured in SAMPLE_CARDS:
            slug = slugify(name)
            _, created = WeddingCard.objects.get_or_create(
                slug=slug,
                defaults={
                    'name':        name,
                    'category':    cats[cat_slug],
                    'palette':     palette,
                    'ornament':    ornament,
                    'price':       price,
                    'is_featured': featured,
                    'is_active':   True,
                    'description': f'Beautiful {cats[cat_slug].name} wedding invitation card.',
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'✔ {count} new cards seeded!'))
