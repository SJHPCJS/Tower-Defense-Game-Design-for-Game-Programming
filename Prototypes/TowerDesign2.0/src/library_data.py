# Character Library Data Configuration
# English version with enhanced nature vs urbanization theme

# Character Categories - Forest Alliance vs City Invaders
TOWERS = ["Emberwing", "Volt Cow", "Banana Blaster", "Wood Sage", "Chrono Cactus"]
ENEMIES = ["Wiregeist", "Boxshot", "Adframe", "Caffeinj", "Cementum"]

# Complete Character Library Data
LIBRARY_DATA = {
    # === Forest Alliance - Nature Guardians ===
    "HOME": {
        "name": "Forest Heart",
        "faction": "ally",
        "story": """NATURE SANCTUARY - FOREST GUARDIAN

The ancient life core of the forest, awakened to resist the mechanical invasion from the city. This mystical entity serves as the last bastion of natural magic, channeling the forest's life force to protect all woodland creatures.

When enemies approach, the Forest Heart glows with protective energy. Its presence strengthens nearby forest defenders and provides sanctuary for all who fight to preserve nature's balance.""",
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
        "story": """FLAME GUARDIAN - FOREST PROTECTOR

A majestic fire spirit soaring through forest canopies, wielding ancient flames to incinerate mechanical invaders. Born from sacred fire groves, Emberwing serves as the forest's primary ranged defender.

This aerial guardian launches concentrated fire projectiles that deal massive damage to armored enemies. Its flames burn with pure natural essence, making it especially effective against synthetic materials and robotic constructs.""",
        "stats": {
            "Damage": "45",
            "Attack Rate": "0.9 sec",
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
        "story": """THUNDER BEAST - FOREST PROTECTOR

A powerful bovine spirit infused with lightning magic, standing as the forest's heavy artillery. Once a peaceful meadow guardian, Volt Cow has channeled storm energy to become a formidable defender against technological threats.

This electrified protector generates devastating electrical attacks that overload electronic systems and disable multiple enemies simultaneously. Its thunder echoes through the forest, warning all invaders of nature's wrath.""",
        "stats": {
            "Damage": "65", 
            "Attack Rate": "1.2 sec",
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
        "story": """RAPID DEFENDER - FOREST PROTECTOR

A quirky yet effective forest defender that harnesses tropical fruit power. This enthusiastic guardian launches rapid-fire banana projectiles with surprising accuracy and speed.

Despite its playful appearance, Banana Blaster poses a serious threat to fast-moving enemies. Its high fire rate makes it perfect for intercepting quick scouts and overwhelming weaker invader groups with constant organic ammunition barrages.""",
        "stats": {
            "Damage": "25",
            "Attack Rate": "0.3 sec", 
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
        "story": """NATURE MYSTIC - FOREST PROTECTOR

An ancient tree spirit versed in the deep magic of the forest. Wood Sage channels centuries of wisdom and natural energy to protect the woodland realm from artificial corruption.

This wise defender combines solid damage output with natural resilience. Its root network draws power directly from the earth, making it a reliable and cost-effective guardian embodying nature's enduring strength.""",
        "stats": {
            "Damage": "35",
            "Attack Rate": "0.8 sec",
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
        "story": """TIME WARDEN - FOREST PROTECTOR

A mystical desert spirit that has mastered temporal magic to aid forest defense. This spiny guardian doesn't deal direct damage but manipulates time itself to hinder enemy advances.

Chrono Cactus creates temporal distortion fields that slow all nearby enemies by 25%. Its strategic value is immense, giving other defenders more time to eliminate threats and creating tactical advantages across the battlefield.""",
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
    
    # === City Invaders - Urban Forces ===
    "Wiregeist": {
        "name": "Wiregeist",
        "faction": "enemy",
        "story": """ELECTRICAL PHANTOM - CITY INVADER

A malevolent spirit born from discarded electronics and urban electromagnetic pollution. This ghostly entity leads technological assault against the natural world, seeking to corrupt all organic life with digital chaos.

Fast and elusive, Wiregeist phases through organic defenses while maintaining deadly electrical attacks. Its presence destabilizes natural order, making it a priority target for forest defenders.""",
        "stats": {
            "Health": "140",
            "Speed": "55", 
            "Faction": "City Invaders",
            "Kill Reward": "$4",
            "Base Damage": "1 HP",
            "Special Ability": "Aura: +20% speed to nearby enemies"
        },
        "sprite_path": "assets/sprite/enemy/wiregeist.png",
        "portrait_path": "assets/library/enemy/Wiregeist.png"
    },
    
    "Boxshot": {
        "name": "Boxshot", 
        "faction": "enemy",
        "story": """DELIVERY DRONE - CITY INVADER

An autonomous delivery bot reprogrammed for invasion. These mass-produced units flood the forest with sheer numbers, carrying packages of urban pollution and synthetic materials.

Moderate in strength and speed, Boxshots represent the relentless march of commercialization. They methodically advance through natural barriers, delivering toxic cargo to contaminate pristine wilderness areas.""",
        "stats": {
            "Health": "160",
            "Speed": "50",
            "Faction": "City Invaders", 
            "Kill Reward": "$2",
            "Base Damage": "1 HP",
            "Special Ability": "Steady advance"
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
            "Health": "200", 
            "Speed": "50",
            "Faction": "City Invaders",
            "Kill Reward": "$3",
            "Base Damage": "1 HP",
            "Special Ability": "30% dodge chance"
        },
        "sprite_path": "assets/sprite/enemy/adframe.png",
        "portrait_path": "assets/library/enemy/Adframe.png"
    },
    
    "Caffeinj": {
        "name": "Caffeinj",
        "faction": "enemy",
        "story": """HYPER SCOUT - CITY INVADER

An over-caffeinated reconnaissance unit powered by concentrated urban stimulants. These jittery scouts zip through the forest at incredible speeds, mapping weak points in natural defenses.

Extremely fast but fragile, Caffeinj units rely on speed and unpredictable movement patterns. Their hyperactive behavior makes them difficult to track, often slipping past slower defensive measures.""",
        "stats": {
            "Health": "120",
            "Speed": "90",
            "Faction": "City Invaders",
            "Kill Reward": "$2", 
            "Base Damage": "1 HP",
            "Special Ability": "Ultra-fast movement, erratic path"
        },
        "sprite_path": "assets/sprite/enemy/caffeinj.png",
        "portrait_path": "assets/library/enemy/Caffeinj.png"
    },
    
    "Cementum": {
        "name": "Cementum",
        "faction": "enemy",
        "story": """HEAVY CONSTRUCTOR - CITY INVADER

A massive construction mech designed to pave over natural landscapes and erect concrete structures. These heavily armored units represent the ultimate goal of urban expansion - total environmental transformation.

Slow but incredibly durable, Cementum units absorb enormous damage while steadily advancing. Each step leaves concrete residue, permanently altering the forest floor and threatening to turn green spaces into urban wastelands.""",
        "stats": {
            "Health": "400",
            "Speed": "30", 
            "Faction": "City Invaders",
            "Kill Reward": "$5",
            "Base Damage": "2 HP",
            "Special Ability": "Heavy armor, terrain modification"
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