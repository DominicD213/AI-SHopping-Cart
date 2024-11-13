import re
from spellchecker import SpellChecker
from sqlalchemy import text

# Clothing corrections dictionary
clothing_corrections = {
    "tshirt": ["t-shirt", "tee shirt", "tee-shirt", "t shirt", "teeshirt"],
    "shoes": ["sneakers", "trainers", "loafers", "tennis shoes", "athletic shoes", "sneaker", "footwear", "boots"],
    "sweatshirt": ["hoodie", "hoody", "crewneck", "sweater shirt", "jumper", "pullover"],
    "sweatpants": ["jogging pants", "joggers", "track pants", "jog pants", "warm-up pants", "jog", "lounge pants"],
    "jeans": ["denims", "denim jeans", "blue jeans", "skinny jeans", "flared jeans", "straight jeans", "bootcut jeans"],
    "pants": ["trousers", "slacks", "chinos", "khakis", "dress pants", "casual pants", "cargo pants", "work pants"],
    "beanie": ["knit cap", "beenie", "winter hat", "ski hat", "watch cap"],
    "sweater": ["jumper", "pullover", "cardy", "cardi", "cardigan"],
    "puffer": ["puffer jacket", "down jacket", "quilted jacket", "puffy coat"],
    "bomber": ["bomber jacket", "flight jacket", "aviator jacket"],
    "pajamas": ["pjs", "pj's", "nightwear", "sleepwear", "jammies", "bedclothes", "nightdress", "loungewear"],
    "blazer": ["suit jacket", "sports coat", "formal jacket", "business jacket"],
    "sweatsuit": ["tracksuit", "athletic suit", "track suit", "warm-up suit", "training suit"],
    "tank": ["tank top", "singlet", "vest top", "athletic tank", "workout tank", "sleeveless top"],
    "heels": ["high heels", "stiletto", "pumps", "kitten heels", "platform heels", "wedge heels"],
    "boots": ["ankle boots", "combat boots", "work boots", "hiking boots", "riding boots", "chelsea boots"],
    "parka": ["parka jacket", "winter coat", "fur-lined parka", "heavy parka"],
    "sandals": ["sandles", "flip flop", "flip-flops", "open-toe shoes", "thongs", "beach sandals", "slides"],
    "button-up": ["button up", "button-down", "dress shirt", "oxford shirt", "formal shirt", "collared shirt", "button front shirt"],
    "cargo": ["cargo pants", "utility pants", "multi-pocket pants"],
    "romper": ["romper suit", "playsuit", "one-piece suit", "jumpsuit", "shortall"],
    "pinafore": ["pinafore dress", "apron dress", "smock dress"],
    "overalls": ["dungarees", "coveralls", "bib overalls", "mechanic overalls", "utility overalls"],
    "swimsuit": ["swim trunks", "bathing suit", "swimming trunks", "board shorts", "one-piece", "two-piece", "bikini"],
    "leggings": ["yoga pants", "tights", "workout pants", "compression pants", "sports leggings", "activewear"],
    "vest": ["waistcoat", "gilet", "sleeveless jacket", "formal vest", "puffer vest"],
    "scarf": ["wrap", "shawl", "neck scarf", "fashion scarf", "muffler"],
    "gloves": ["mittens", "hand warmers", "winter gloves", "fingerless gloves", "driving gloves"]
}

# Synonym map for category matching
SYNONYM_MAP = {
    "Movie": ["film", "cinema", "action", "sci-fi", "drama", "documentary", "thriller", "comedy", "horror", "romance", "animation", "biopic"],
    "Book": ["novel", "literature", "classic", "fiction", "non-fiction", "biography", "textbook", "manga", "graphic novel", "manual", "guide", "storybook"],
    "Clothing": ["tshirt", "hoodie", "jacket", "jeans", "pants", "sweater", "dress", "skirt", "blouse", "suit", "outerwear", "top", "bottom", "footwear"],
    "Electronics": ["gadget", "device", "smartphone", "laptop", "tablet", "camera", "headphones", "speaker", "monitor", "console", "tv", "earbuds"],
    "Furniture": ["chair", "table", "sofa", "couch", "bed", "desk", "bookshelf", "cabinet", "dining set", "stool", "recliner", "bench", "wardrobe"],
    "Food": ["snack", "organic", "gluten-free", "grocery", "fruit", "vegetable", "beverage", "meat", "dairy", "grain", "seafood", "sauce", "spice"]
}

# Prohibited keywords for content filtering
prohibited_keywords = set([
    "cocaine", "heroin", "methamphetamine", "ecstasy", "lsd", "fentanyl", "amphetamine", "opium", "crack",
    "pistol", "handgun", "firearm", "grenade", "explosives", "dynamite", "bomb", "incendiary", "c4", "detonator",
    "silencer", "smg", "rifle", "ak47", "uzi", "glock", "sniper", "shotgun", "machete", "switchblade",
    "dirk", "butterfly", "knuckleduster", "brass", "cyanide", "arsenic", "ricin", "strychnine", "sarin",
    "mustard", "nerve", "counterfeit", "fake", "forged", "stolen", "skimmer", "trafficking", "contraband",
    "cartel", "narcotics", "cannabis", "marijuana", "weed", "hashish", "opiate", "barbiturate",
    "meth", "lab", "drug", "blackmail", "extortion", "bribery", "espionage", "spy", "malware",
    "virus", "cyberattack", "ransomware", "keylogger", "trojan", "worm", "sexting", "pornography", 
    "revenge", "voyeurism", "adoption", "organ", "body", "human", "abuse", "child", "underage",
    "sex", "pedo", "incest", "rape", "hitman", "assassin", "torture", "execution", "contract",
    "skimmer", "money", "laundering", "paraphernalia", "needle", "syringe", "bong", "pipe",
    "heroin", "opium", "oxycodone", "hydrocodone", "vicodin", "percocet", "adderall", "xanax",
    "revolver", "trafficking", "sex", "slave", "dmt", "molotov"
])

def validate_input(input_str: str, location: int, db_connection):
    """
    Validates and categorizes input based on location context.

    Parameters:
    - input_str (str): User's input to validate.
    - location (int): Location code indicating input type (0-9).
    - db_connection: Database connection for category matching.

    Returns:
    - tuple: (int, list) with the number of distinct search terms and a product array.
      - product_array format: [validated_term, original_term, status]
    """
    spell = SpellChecker()

    # Spell-check term
    def spell_check_and_correct(term):
        return " ".join([spell.correction(word) for word in term.split()])

    # Category matching in the database
    def get_category_from_database(term):
        query = text("SELECT category FROM products WHERE tags LIKE :term LIMIT 1")
        result = db_connection.execute(query, {"term": f"%{term}%"}).first()
        return result[0] if result else None

    # Match with synonyms
    def get_category_from_synonyms(term):
        for category, synonyms in SYNONYM_MAP.items():
            if term in synonyms:
                return category
        return None

    # Split and categorize search terms
    def split_and_categorize_search(input_str):
        terms = re.split(r'\band\b|,|\bwith\b', input_str.lower())
        terms = [term.strip() for term in terms if term.strip()]
        product_array = []

        for term in terms:
            original_term = term
            term = spell_check_and_correct(term)

            # Check for prohibited terms
            if any(keyword in term.lower() for keyword in prohibited_keywords):
                product_array.append(["", original_term, 2])
                continue

            # Category matching
            category = get_category_from_database(term) or get_category_from_synonyms(term)
            validated_term = category.lower() if category else ""
            status = 0 if category else 2
            product_array.append([validated_term, original_term, status])

        return len(product_array), product_array

    # Location-based logic
    if location == 0:  # General Search
        return split_and_categorize_search(input_str)

    elif location == 1:  # Clothing-specific Search
        terms = input_str.split()
        validated_terms = []
        for term in terms:
            for base_term, synonyms in clothing_corrections.items():
                if term.lower() in synonyms:
                    validated_terms.append(base_term)
                    break
            else:
                validated_terms.append(spell_check_and_correct(term))
        corrected = " ".join(validated_terms)
        return 1, [[corrected, input_str, 1 if corrected.lower() != input_str.lower() else 0]]

    elif 2 <= location <= 4:  # Books, Movies, Illegal Items
        if location == 4:
            return 1, [["", input_str, 2]]
        return 1, [[input_str, input_str, 0]]

    # Default non-applicable
    return 1, [["", input_str, 3]]
