# Core/units.py

from Core.logger import setup_logger

logger = setup_logger()

# --- (Tu código de conversiones existente no cambia) ---

# Conversion factors to base units
# Base units: grams for weight, ml for volume, units for count
CONVERSIONS = {
    'weight': {
        'g': 1,
        'kg': 1000,
        'lb': 453.592, # approximate
        'oz': 28.3495, # approximate
    },
    'volume': {
        'ml': 1,
        'lt': 1000,
    },
    'count': {
        'unit': 1,
        'decen':10,
        'docen': 12,
    }
}

def get_base_unit(category):
    if category == 'weight':
        return 'g'
    elif category == 'volume':
        return 'ml'
    elif category == 'count':
        return 'unit'
    else:
        logger.error(f"Unknown category: {category}")
        return None

def convert_to_base(quantity, unit):
    """ Convert quantity to base unit. Returns (converted_quantity, base_unit) or (None, None) if error. """
    try:
        quantity = float(quantity)
        unit = unit.lower()
        for category, factors in CONVERSIONS.items():
            if unit in factors:
                base_unit = get_base_unit(category)
                converted = quantity * factors[unit]
                logger.debug(f"Converted {quantity} {unit} to {converted} {base_unit}")
                return converted, base_unit
        logger.error(f"Unit {unit} not recognized")
        return None, None
    except ValueError as e:
        logger.error(f"Error converting quantity: {e}")
        return None, None

def convert_from_base(quantity, from_unit, to_unit):
    """ Convert from base unit to another unit. """
    try:
        quantity = float(quantity)
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        # Find category
        category = None
        for cat, factors in CONVERSIONS.items():
            if from_unit in factors:
                category = cat
                break
        if not category or to_unit not in CONVERSIONS[category]:
            logger.error(f"Cannot convert from {from_unit} to {to_unit}")
            return None
        # Convert to base first if not already
        if from_unit != get_base_unit(category):
            quantity, _ = convert_to_base(quantity, from_unit)
        # Then to target
        factor = CONVERSIONS[category][to_unit]
        converted = quantity / factor
        logger.debug(f"Converted {quantity} {get_base_unit(category)} to {converted} {to_unit}")
        return converted
    except ValueError as e:
        logger.error(f"Error converting: {e}")
        return None

# --- NUEVA FUNCIÓN AÑADIDA AQUÍ ---

def calculate_cost_per_base_unit(item_data: dict) -> dict:
    """
    Calculates the cost per base unit (e.g., cost per gram) for a given inventory item.

    Args:
        item_data (dict): A dictionary containing item information from the database.
                          Expected keys: 'cantidad_granel', 'cantidad_paquetes',
                                         'unidad', 'total_precio'.

    Returns:
        dict: The original item_data dictionary, but with the 'costo_promedio'
              key updated to the cost per base unit (e.g., cost/gram).
              Returns 0 if calculation is not possible.
    """
    # 1. Obtener la cantidad total y el precio total del diccionario
    total_quantity_bulk = item_data.get('cantidad_granel', 0)
    total_quantity_packages = item_data.get('cantidad_paquetes', 0)
    unidad = item_data.get('unidad')
    total_precio = float(item_data.get('total_precio', 0))

    # 2. Sumar las cantidades para obtener el total físico del producto
    total_physical_quantity = total_quantity_bulk + total_quantity_packages

    # 3. Si no hay cantidad o no hay precio, no se puede calcular el costo
    if not total_physical_quantity or total_precio <= 0 or not unidad:
        logger.warning(f"Skipping cost calculation for item due to missing data: {item_data.get('producto', 'Unknown')}")
        item_data['costo_promedio'] = 0
        return item_data

    # 4. Usar la función convert_to_base que está en este mismo archivo
    converted_quantity, base_unit = convert_to_base(total_physical_quantity, unidad)

    # 5. Calcular el costo por unidad base
    if converted_quantity and converted_quantity > 0:
        cost_per_unit = total_precio / converted_quantity
        logger.info(f"Calculated cost for {item_data.get('producto')}: ${cost_per_unit:.4f} per {base_unit}")
        item_data['costo_promedio'] = cost_per_unit
    else:
        # Si la conversión falla, el costo es 0
        logger.warning(f"Could not convert quantity for item: {item_data.get('producto')}")
        item_data['costo_promedio'] = 0

    return item_data