
TOWERS = ["Emberwing", "Volt Cow", "Banana Blaster", "Wood Sage", "Chrono Cactus"]
ENEMIES = ["Wiregeist", "Boxshot", "Adframe", "Caffeinj", "Cementum"]


LIBRARY_DATA = {
    "HOME": {
        "name": "Forest Heart",
        "faction": "ally",
        "story": """NATURE SANCTUARY - FOREST GUARDIAN

One of the oldest spirits of nature, the Forest Heart once thrived at the center of the wild. However, as urban expansion encroaches deeper into the wilderness, its survival becomes increasingly threatened.

No longer able to defend itself, the Forest Heart now relies on nature's creatures, who rise as guardians to protect their origin spirit. These defenders fight not only for survival, but to preserve the sacred balance of life.""",
        "stats": {
            "Type": "Base Structure",
            "Faction": "Forest Alliance",
            "Health": "Variable (10HP as default)",
            "Special": "Victory Objective",
        },
        "portrait_path": "library/tower/forest spirit.png",
        "sprite_path": "sprite/HOME.png"
    },
    
    "Emberwing": {
        "name": "Emberwing",
        "faction": "ally",
        "story": """FLAME GUARDIAN - FOREST PROTECTOR

A majestic fire spirit soaring through the forest canopy, born from the sacred fire groves. Emberwing channels elemental flame through its wings, unleashing scorching feather projectiles imbued with natural fire magic.

As the forest's primary flame-based defender, it deals moderate initial damage but ignites enemies on impact, causing lasting burn effects. Its presence turns the air searing hot, warning intruders of nature’s wrath.""",
        "stats": {
            "Damage": "45",
            "Attack Rate": "0.9 sec",
            "Faction": "Forest Alliance", 
            "Cost": "$25",
            "Specialty": "Applies burn damage over time"
        },
        "sprite_path": "sprite/tower/emberwing.png",
        "portrait_path": "library/tower/Emberwing.png"
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
            "Faction": "Forest Alliance",
            "Cost": "$25",
            "Specialty": "Lightning damage that arcs to nearby enemies"
        },
        "sprite_path": "sprite/tower/volt cow.png",
        "portrait_path": "library/tower/Volt Cow.png"
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
            "Faction": "Forest Alliance",
            "Cost": "$20",
            "Specialty": "Rapid fire attacks"
        },
        "sprite_path": "sprite/tower/banana blaster.png",
        "portrait_path": "library/tower/Banana Blaster.png"
    },
    
    "Wood Sage": {
        "name": "Wood Sage",
        "faction": "ally",
        "story": """NATURE MYSTIC - FOREST PROTECTOR

A fusion of ancient wood elemental and great forest ape, Wood Sage embodies both nature’s wisdom and raw primal strength. Born in the heart of an overgrown jungle, it moves with the patience of trees and strikes with the fury of beasts.

Its wooden limbs are fortified by centuries-old bark, and its fists channel the pulse of the forest. Combining durability with solid attack power, Wood Sage is a steadfast defender who roots itself into battle to shield the wild.""",
        "stats": {
            "Damage": "35",
            "Attack Rate": "0.8 sec",
            "Faction": "Forest Alliance",
            "Cost": "$15",
            "Specialty": "Balanced performance"
        },
        "sprite_path": "sprite/tower/wood sage.png",
        "portrait_path": "library/tower/Wood Sage.png"
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
        "sprite_path": "sprite/tower/chrono cactus.png",
        "portrait_path": "library/tower/Chrono Cactus.png"
    },

    "Wiregeist": {
        "name": "Wiregeist",
        "faction": "enemy",
        "story": """ELECTRICAL PHANTOM - CITY INVADER

A volatile specter formed from tangled wires, broken circuits, and abandoned transmissions. Wiregeist embodies the restless current of a hyperconnected world, and flows like electricity through the ranks of the urban invasion force.

Rather than attacking directly, it emits a pulsing electromagnetic field that boosts the movement speed of nearby allies. Wherever it floats, the air crackles, and its presence turns sluggish formations into fast-moving storms of disruption.""",
        "stats": {
            "Health": "140",
            "Speed": "55", 
            "Faction": "City Invaders",
            "Kill Reward": "$4",
            "Base Damage": "1 HP",
            "Special Ability": "Aura: +20% speed to nearby enemies"
        },
        "sprite_path": "sprite/enemy/wiregeist.png",
        "portrait_path": "library/enemy/Wiregeist.png"
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
        "sprite_path": "sprite/enemy/boxshot.png",
        "portrait_path": "library/enemy/Boxshot.png"
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
        "sprite_path": "sprite/enemy/adframe.png",
        "portrait_path": "library/enemy/Adframe.png"
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
        "sprite_path": "sprite/enemy/caffeinj.png",
        "portrait_path": "library/enemy/Caffeinj.png"
    },
    
    "Cementum": {
        "name": "Cementum",
        "faction": "enemy",
        "story": """HEAVY CONSTRUCTOR - CITY INVADER

A colossal construction mech forged from steel, cement, and industrial ambition. Cementum is the embodiment of brute urban force—built not for speed, but for unstoppable advance.

With overwhelming armor and the highest durability among the invasion force, it can withstand an extraordinary amount of damage. Though slow, its sheer presence pressures defenders and demands focused fire to prevent it from crushing the forest's final line of defense.""",
        "stats": {
            "Health": "400",
            "Speed": "30", 
            "Faction": "City Invaders",
            "Kill Reward": "$5",
            "Base Damage": "2 HP",
            "Special Ability": "Heavy armor, terrain modification"
        },
        "sprite_path": "sprite/enemy/cementum.png",
        "portrait_path": "library/enemy/Cementum.png"
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