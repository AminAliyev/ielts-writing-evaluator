from django.core.management.base import BaseCommand
from products.models import Category, Tea, TasterBoxConfig


class Command(BaseCommand):
    help = "Seed sample Azerbaijani teas"

    def handle(self, *args, **kwargs):
        black, _ = Category.objects.get_or_create(name="Black Tea", defaults={"description": "Rich and malty.", "order": 1})
        green, _ = Category.objects.get_or_create(name="Green Tea", defaults={"description": "Fresh and vegetal.", "order": 2})
        white, _ = Category.objects.get_or_create(name="White Tea", defaults={"description": "Light and floral.", "order": 3})
        herbal, _ = Category.objects.get_or_create(name="Herbal", defaults={"description": "Caffeine-free blends.", "order": 4})

        teas = [
            ("Lankaran Black Gold", black, "Flagship estate black tea"),
            ("Astara Morning Mist", green, "Delicate spring green"),
            ("Caspian Breeze", white, "Silvery white tea"),
            ("Highland Herbal", herbal, "Aromatic mountain blend"),
            ("First Flush Reserve", black, "Seasonal first flush"),
            ("Talysh Garden", green, "Garden-fresh green"),
            ("Lerik Wild", herbal, "Wild herb infusion"),
            ("Masalli Sunrise", black, "Bold breakfast black"),
        ]
        created = []
        for idx, (name, category, tagline) in enumerate(teas, start=1):
            tea, _ = Tea.objects.get_or_create(
                name=name,
                defaults={
                    "category": category,
                    "tagline": tagline,
                    "description": f"{name} is crafted in small lots from hand-picked leaves in Azerbaijan.",
                    "story": f"{name} carries family harvesting traditions from Lankaran highlands.",
                    "origin": "Lankaran Highlands, Azerbaijan",
                    "altitude": "600-800m",
                    "harvest_season": "Spring",
                    "tasting_notes": ["honey", "wild herbs", "warm finish"],
                    "brewing_temp": "85-90°C",
                    "brewing_time": "3-5 minutes",
                    "weight_options": [{"grams": 100, "price": "24.00"}, {"grams": 250, "price": "55.00"}],
                    "price_per_kg": 220 + idx,
                    "is_featured": idx <= 3,
                    "available_harvest_seasons": ["Spring 2027", "Autumn 2027"],
                },
            )
            created.append(tea)

        box, _ = TasterBoxConfig.objects.get_or_create(
            name="Naqqash Tea Taster Box",
            defaults={"description": "A curated introduction to Naqqash Tea.", "price": "42.00", "currency": "USD"},
        )
        box.teas.set(created[:5])
        self.stdout.write(self.style.SUCCESS("Seeded tea catalogue and taster box."))
