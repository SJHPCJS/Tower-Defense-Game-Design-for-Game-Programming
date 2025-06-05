# Character Library Data Configuration
# English version for professional presentation

# Character Categories - Forest Alliance vs City Invaders
TOWERS = ["Emberwing", "Volt Cow", "Banana Blaster", "Wood Sage", "Chrono Cactus"]
ENEMIES = ["Wiregeist", "Boxshot", "Adframe", "Caffeinj", "Cementum"]

# Complete Character Library Data
LIBRARY_DATA = {
    # === Forest Alliance - Allied Spirits ===
    "HOME": {
        "name": "Forest Spirit",
        "faction": "ally",
        "story": """FOREST GUARDIAN - ALLIED SPIRIT

The ancient heart of the forest, awakened to defend against the mechanical invasion from the city. This mystical entity serves as the last bastion of natural magic, channeling the forest's life force to protect all woodland creatures.

When enemies approach, the Forest Spirit glows with protective energy. Its very presence strengthens nearby forest defenders and provides sanctuary for all who fight to preserve nature's balance.""",
        "stats": {
            "Type": "Base Structure",
            "Faction": "Forest Alliance",
            "Health": "Variable (10-20 HP)",
            "Special": "Victory Objective",
            "Ability": "Strengthens nearby allies"
        },
        "portrait_path": "assets/library/tower/forest spirit.png",
        "sprite_path": "assets/sprite/HOME.png"
    },
    
    "Emberwing": {
        "name": "Emberwing",
        "faction": "ally",
        "story": """FLAME GUARDIAN - ALLIED SPIRIT

A majestic fire spirit that soars through the forest canopy, wielding ancient flames to incinerate mechanical invaders. Born from the sacred fire groves, Emberwing serves as the forest's primary ranged defender.

This aerial guardian launches concentrated fire projectiles that deal significant damage to armored enemies. Its flames burn with the pure essence of nature, making it especially effective against synthetic materials and robotic constructs.""",
        "stats": {
            "Damage": "45",
            "Rate of Fire": "0.9 sec",
            "Range": "Medium",
            "Faction": "Forest Alliance", 
            "Cost": "$25",
            "Specialty": "Anti-armor attacks"
        },
        "sprite_path": "assets/sprite/tower/emberwing.png",
        "portrait_path": "assets/library/tower/Emberwing.png"
    },
    
    "Volt Cow": {
        "name": "Volt Cow", 
        "faction": "ally",
        "story": """THUNDER BEAST - ALLIED SPIRIT

A powerful bovine spirit infused with lightning magic, standing as the forest's heavy artillery. Once a peaceful meadow guardian, Volt Cow has channeled storm energy to become a formidable defender against technological threats.

This electrified protector generates devastating electrical attacks that can overload electronic systems and disable multiple enemies simultaneously. Its thunder strikes echo through the forest, warning all invaders of nature's wrath.""",
        "stats": {
            "Damage": "65", 
            "Rate of Fire": "1.2 sec",
            "Range": "Long",
            "Faction": "Forest Alliance",
            "Cost": "$25",
            "Specialty": "Heavy damage dealer"
        },
        "sprite_path": "assets/sprite/tower/volt cow.png",
        "portrait_path": "assets/library/tower/Volt Cow.png"
    },
    
    "Banana Blaster": {
        "name": "Banana Blaster",
        "faction": "ally",
        "story": """RAPID DEFENDER - ALLIED SPIRIT

A quirky yet effective forest defender that harnesses the power of tropical fruits. This enthusiastic guardian launches rapid-fire banana projectiles with surprising accuracy and speed.

Despite its playful appearance, the Banana Blaster is a serious threat to fast-moving enemies. Its high rate of fire makes it perfect for intercepting quick scouts and overwhelming groups of weaker invaders with a constant barrage of organic ammunition.""",
        "stats": {
            "Damage": "25",
            "Rate of Fire": "0.3 sec", 
            "Range": "Medium",
            "Faction": "Forest Alliance",
            "Cost": "$20",
            "Specialty": "Rapid fire attacks"
        },
        "sprite_path": "assets/sprite/tower/banana blaster.png",
        "portrait_path": "assets/library/tower/Banana Blaster.png"
    },
    
    "Wood Sage": {
        "name": "Wood Sage",
        "faction": "ally",
        "story": """NATURE MYSTIC - ALLIED SPIRIT

An ancient tree spirit versed in the deep magic of the forest. The Wood Sage channels centuries of wisdom and natural energy to protect the woodland realm from artificial corruption.

This wise defender combines solid damage output with natural resilience. Its root network allows it to draw power directly from the earth, making it a reliable and cost-effective guardian that embodies the enduring strength of nature.""",
        "stats": {
            "Damage": "35",
            "Rate of Fire": "0.8 sec",
            "Range": "Medium", 
            "Faction": "Forest Alliance",
            "Cost": "$15",
            "Specialty": "Balanced performance"
        },
        "sprite_path": "assets/sprite/tower/wood sage.png",
        "portrait_path": "assets/library/tower/Wood Sage.png"
    },
    
    "Chrono Cactus": {
        "name": "Chrono Cactus",
        "faction": "ally",
        "story": """TIME WARDEN - ALLIED SPIRIT

A mystical desert spirit that has mastered temporal magic to aid the forest's defense. This spiny guardian doesn't deal direct damage but instead manipulates time itself to hinder enemy advances.

The Chrono Cactus creates temporal distortion fields that slow all nearby enemies by 25%. Its strategic value is immense, giving other defenders more time to eliminate threats and creating tactical advantages across the battlefield.""",
        "stats": {
            "Damage": "0 (Support)",
            "Slow Effect": "25%",
            "Slow Range": "5 tiles",
            "Faction": "Forest Alliance", 
            "Cost": "$25",
            "Specialty": "Area slow support"
        },
        "sprite_path": "assets/sprite/tower/chrono cactus.png",
        "portrait_path": "assets/library/tower/Chrono Cactus.png"
    },
    
    # === City Invaders - Enemy Forces ===
    "Wiregeist": {
        "name": "Wiregeist",
        "faction": "enemy",
        "story": """ELECTRICAL PHANTOM - CITY INVADER

A malevolent spirit born from discarded electronics and urban electromagnetic pollution. This ghostly entity leads the technological assault against the natural world, seeking to corrupt all organic life with digital chaos.

Fast and elusive, the Wiregeist phases through organic defenses while maintaining deadly electrical attacks. Its presence destabilizes the natural order, making it a priority target for forest defenders.""",
        "stats": {
            "Health": "Medium",
            "Speed": "Fast", 
            "Faction": "City Invaders",
            "Reward": "$4",
            "Damage to Base": "1 HP",
            "Ability": "Electrical interference"
        },
        "sprite_path": "assets/sprite/enemy/wiregeist.png",
        "portrait_path": "assets/library/enemy/Wiregeist.png"
    },
    
    "Boxshot": {
        "name": "Boxshot", 
        "faction": "enemy",
        "story": """DELIVERY DRONE - CITY INVADER

An autonomous delivery bot reprogrammed for invasion. These mass-produced units flood the forest with their sheer numbers, carrying packages of urban pollution and synthetic materials.

Moderate in strength and speed, Boxshots represent the relentless march of commercialization. They methodically advance through natural barriers, delivering their toxic cargo to contaminate pristine wilderness areas.""",
        "stats": {
            "Health": "Medium",
            "Speed": "Medium",
            "Faction": "City Invaders", 
            "Reward": "$3",
            "Damage to Base": "1 HP",
            "Ability": "Steady advance"
        },
        "sprite_path": "assets/sprite/enemy/boxshot.png",
        "portrait_path": "assets/library/enemy/Boxshot.png"
    },
    
    "Adframe": {
        "name": "Adframe",
        "faction": "enemy",
        "story": """PROPAGANDA UNIT - CITY INVADER

A walking advertisement display designed to spread urban ideology and consumer culture throughout the forest. These units project hypnotic commercial messages intended to seduce woodland creatures into abandoning nature.

Quick and persistent, Adframes use psychological warfare alongside physical invasion. Their bright displays and constant advertising noise pollute the peaceful forest atmosphere, making them particularly disruptive enemies.""",
        "stats": {
            "Health": "Low-Medium", 
            "Speed": "Fast",
            "Faction": "City Invaders",
            "Reward": "$3",
            "Damage to Base": "1 HP",
            "Ability": "Distraction tactics"
        },
        "sprite_path": "assets/sprite/enemy/adframe.png",
        "portrait_path": "assets/library/enemy/Adframe.png"
    },
    
    "Caffeinj": {
        "name": "Caffeinj",
        "faction": "enemy",
        "story": """HYPER SCOUT - CITY INVADER

An over-caffeinated reconnaissance unit powered by concentrated urban stimulants. These jittery scouts zip through the forest at incredible speeds, mapping weak points in natural defenses.

Extremely fast but fragile, Caffeinj units rely on speed and unpredictable movement patterns. Their hyperactive behavior makes them difficult to track, and they often slip past slower defensive measures.""",
        "stats": {
            "Health": "Low",
            "Speed": "Very Fast",
            "Faction": "City Invaders",
            "Reward": "$2", 
            "Damage to Base": "1 HP",
            "Ability": "Erratic movement"
        },
        "sprite_path": "assets/sprite/enemy/caffeinj.png",
        "portrait_path": "assets/library/enemy/Caffeinj.png"
    },
    
    "Cementum": {
        "name": "Cementum",
        "faction": "enemy",
        "story": """HEAVY CONSTRUCTOR - CITY INVADER

A massive construction mech designed to pave over natural landscapes and erect concrete structures. These heavily armored units represent the ultimate goal of urban expansion - total environmental transformation.

Slow but incredibly durable, Cementum units absorb enormous amounts of damage while steadily advancing. Each step leaves behind concrete residue, permanently altering the forest floor and threatening to turn green spaces into urban wastelands.""",
        "stats": {
            "Health": "Very High",
            "Speed": "Slow", 
            "Faction": "City Invaders",
            "Reward": "$5",
            "Damage to Base": "2 HP",
            "Ability": "Heavy armor, terrain modification"
        },
        "sprite_path": "assets/sprite/enemy/cementum.png",
        "portrait_path": "assets/library/enemy/Cementum.png"
    }
}

# Utility functions for character data
def get_character_data(character_name):
    """Get data for specified character"""
    return LIBRARY_DATA.get(character_name, None)

def get_all_towers():
    """Get all tower data"""
    return [(name, LIBRARY_DATA[name]) for name in TOWERS]

def get_all_enemies():
    """Get all enemy data"""
    return [(name, LIBRARY_DATA[name]) for name in ENEMIES] 