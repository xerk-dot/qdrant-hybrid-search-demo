"""Generate sample e-commerce dataset with structured and unstructured data."""

import random
import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class Product:
    """Product data structure combining structured and unstructured data."""
    id: str
    title: str
    description: str  # Unstructured text for semantic search
    category: str
    brand: str
    price: float
    rating: float
    num_reviews: int
    availability: str
    tags: List[str]
    specifications: Dict[str, Any]

class EcommerceDataGenerator:
    """Generate realistic e-commerce product data for the demo."""
    
    def __init__(self):
        self.categories = {
            "Electronics": {
                "subcategories": ["Laptops", "Smartphones", "Headphones", "Cameras", "Smart Home"],
                "brands": ["Apple", "Samsung", "Sony", "Dell", "HP", "Lenovo", "Canon", "Bose"],
                "price_ranges": [(200, 3000), (100, 1500), (50, 500), (300, 2000), (50, 300)]
            },
            "Clothing & Accessories": {
                "subcategories": ["Men's Clothing", "Women's Clothing", "Shoes", "Bags", "Jewelry"],
                "brands": ["Nike", "Adidas", "Levi's", "Calvin Klein", "Coach", "Michael Kors"],
                "price_ranges": [(20, 200), (25, 300), (50, 400), (100, 800), (30, 500)]
            },
            "Sports & Outdoors": {
                "subcategories": ["Fitness Equipment", "Outdoor Gear", "Athletic Wear", "Team Sports"],
                "brands": ["Nike", "Under Armour", "Patagonia", "North Face", "REI", "Garmin"],
                "price_ranges": [(30, 500), (50, 800), (25, 150), (20, 300)]
            },
            "Home & Garden": {
                "subcategories": ["Furniture", "Kitchen", "Bedding", "Garden Tools", "Decor"],
                "brands": ["IKEA", "KitchenAid", "Dyson", "Cuisinart", "Black & Decker"],
                "price_ranges": [(50, 1000), (30, 400), (20, 200), (25, 150), (15, 300)]
            }
        }
        
        self.description_templates = {
            "Electronics": [
                "Experience cutting-edge technology with this high-performance {subcategory}. Features advanced {feature1} and {feature2} for {benefit}.",
                "Professional-grade {subcategory} designed for {use_case}. Includes {feature1}, {feature2}, and exceptional {quality_aspect}.",
                "Innovative {subcategory} that combines {feature1} with {feature2} to deliver {benefit}. Perfect for {target_user}."
            ],
            "Clothing & Accessories": [
                "Premium {subcategory} crafted from high-quality {material}. Features {feature1} and {feature2} for ultimate {benefit}.",
                "Stylish and comfortable {subcategory} perfect for {occasion}. Made with {material} and designed for {benefit}.",
                "Trendy {subcategory} that combines fashion with functionality. Features {feature1} and {feature2}."
            ],
            "Sports & Outdoors": [
                "High-performance {subcategory} engineered for {activity}. Built with {material} technology for {benefit}.",
                "Professional {subcategory} designed for serious athletes. Features {feature1} and {feature2} for maximum {benefit}.",
                "Durable {subcategory} perfect for outdoor adventures. Weather-resistant design with {feature1} and {feature2}."
            ],
            "Home & Garden": [
                "Essential {subcategory} that brings {benefit} to your home. Features {feature1} and {feature2} for convenience.",
                "Elegant {subcategory} designed to enhance your living space. Combines {feature1} with {feature2}.",
                "Practical {subcategory} that makes daily life easier. Built with {material} and includes {feature1}."
            ]
        }
        
        self.features_by_category = {
            "Electronics": ["wireless connectivity", "long battery life", "4K resolution", "fast processing", "compact design", "water resistance"],
            "Clothing & Accessories": ["moisture-wicking fabric", "ergonomic fit", "UV protection", "breathable material", "stain resistance", "wrinkle-free"],
            "Sports & Outdoors": ["GPS tracking", "heart rate monitoring", "waterproof design", "lightweight construction", "shock absorption", "adjustable settings"],
            "Home & Garden": ["energy efficiency", "easy installation", "multiple settings", "compact storage", "remote control", "automatic operation"]
        }

    def generate_products(self, num_products: int = 1000) -> List[Product]:
        """Generate a list of realistic product data."""
        products = []
        
        for i in range(num_products):
            category = random.choice(list(self.categories.keys()))
            category_data = self.categories[category]
            
            subcategory = random.choice(category_data["subcategories"])
            brand = random.choice(category_data["brands"])
            
            # Generate price based on category
            price_range = random.choice(category_data["price_ranges"])
            price = round(random.uniform(price_range[0], price_range[1]), 2)
            
            # Generate ratings and reviews
            rating = round(random.uniform(3.0, 5.0), 1)
            num_reviews = random.randint(10, 5000)
            
            # Generate availability
            availability = random.choices(
                ["In Stock", "Limited Stock", "Out of Stock"],
                weights=[0.7, 0.2, 0.1]
            )[0]
            
            # Generate description using templates
            description = self._generate_description(category, subcategory)
            
            # Generate title
            title = f"{brand} {subcategory} - Professional Grade"
            if random.random() > 0.7:
                title += f" {random.choice(['Pro', 'Max', 'Elite', 'Premium', 'Ultra'])}"
            
            # Generate tags
            tags = self._generate_tags(category, subcategory, brand)
            
            # Generate specifications
            specs = self._generate_specifications(category, subcategory)
            
            product = Product(
                id=f"prod_{i+1:04d}",
                title=title,
                description=description,
                category=category,
                brand=brand,
                price=price,
                rating=rating,
                num_reviews=num_reviews,
                availability=availability,
                tags=tags,
                specifications=specs
            )
            
            products.append(product)
        
        return products
    
    def _generate_description(self, category: str, subcategory: str) -> str:
        """Generate realistic product description."""
        template = random.choice(self.description_templates[category])
        features = random.sample(self.features_by_category[category], 2)
        
        replacements = {
            "subcategory": subcategory.lower(),
            "feature1": features[0],
            "feature2": features[1],
            "benefit": random.choice(["performance", "comfort", "durability", "convenience", "style"]),
            "use_case": random.choice(["professionals", "enthusiasts", "daily use", "heavy workloads"]),
            "quality_aspect": random.choice(["build quality", "performance", "reliability"]),
            "target_user": random.choice(["professionals", "enthusiasts", "beginners", "power users"]),
            "material": random.choice(["premium materials", "advanced composites", "high-grade steel", "organic cotton"]),
            "occasion": random.choice(["work", "casual wear", "special events", "daily activities"]),
            "activity": random.choice(["running", "hiking", "training", "competitive sports"])
        }
        
        description = template
        for key, value in replacements.items():
            description = description.replace(f"{{{key}}}", value)
        
        return description
    
    def _generate_tags(self, category: str, subcategory: str, brand: str) -> List[str]:
        """Generate relevant tags for the product."""
        base_tags = [category.lower().replace(" & ", "-"), subcategory.lower().replace(" ", "-"), brand.lower()]
        
        additional_tags = {
            "Electronics": ["tech", "gadget", "digital", "smart", "wireless"],
            "Clothing & Accessories": ["fashion", "style", "comfort", "trendy", "casual"],
            "Sports & Outdoors": ["fitness", "outdoor", "athletic", "performance", "training"],
            "Home & Garden": ["home", "decor", "practical", "convenient", "lifestyle"]
        }
        
        extra_tags = random.sample(additional_tags[category], random.randint(2, 4))
        return base_tags + extra_tags
    
    def _generate_specifications(self, category: str, subcategory: str) -> Dict[str, Any]:
        """Generate category-specific specifications."""
        specs = {}
        
        if category == "Electronics":
            specs.update({
                "warranty": f"{random.randint(1, 3)} years",
                "weight": f"{random.uniform(0.5, 5.0):.1f} lbs",
                "color_options": random.randint(2, 6)
            })
            if "laptop" in subcategory.lower():
                specs.update({
                    "screen_size": f"{random.choice([13.3, 14, 15.6, 17.3])}\",
                    "ram": f"{random.choice([8, 16, 32])}GB",
                    "storage": f"{random.choice([256, 512, 1024])}GB SSD"
                })
        
        elif category == "Clothing & Accessories":
            specs.update({
                "material": random.choice(["Cotton", "Polyester", "Wool", "Synthetic Blend"]),
                "care_instructions": "Machine washable",
                "sizes_available": "XS-XXL"
            })
        
        elif category == "Sports & Outdoors":
            specs.update({
                "weather_resistance": random.choice(["Water-resistant", "Waterproof", "Weather-sealed"]),
                "weight": f"{random.uniform(0.2, 10.0):.1f} lbs"
            })
        
        elif category == "Home & Garden":
            specs.update({
                "dimensions": f"{random.randint(10, 50)}\" x {random.randint(10, 50)}\" x {random.randint(5, 30)}\"",
                "material": random.choice(["Wood", "Metal", "Plastic", "Composite"]),
                "assembly_required": random.choice([True, False])
            })
        
        return specs

    def save_to_json(self, products: List[Product], filename: str = "products.json"):
        """Save products to JSON file."""
        products_dict = []
        for product in products:
            product_dict = {
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "category": product.category,
                "brand": product.brand,
                "price": product.price,
                "rating": product.rating,
                "num_reviews": product.num_reviews,
                "availability": product.availability,
                "tags": product.tags,
                "specifications": product.specifications
            }
            products_dict.append(product_dict)
        
        with open(filename, 'w') as f:
            json.dump(products_dict, f, indent=2)
        
        print(f"Saved {len(products)} products to {filename}")

if __name__ == "__main__":
    generator = EcommerceDataGenerator()
    products = generator.generate_products(1000)
    generator.save_to_json(products)
    
    # Print some sample products
    print("\nSample products generated:")
    for i, product in enumerate(products[:3]):
        print(f"\n{i+1}. {product.title}")
        print(f"   Category: {product.category}")
        print(f"   Price: ${product.price}")
        print(f"   Description: {product.description}")
        print(f"   Tags: {', '.join(product.tags[:5])}")
