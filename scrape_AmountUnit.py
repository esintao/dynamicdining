import re
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize your driver (adjust for Chrome/Firefox as needed)
driver = webdriver.Chrome()
driver.get("https://www.food.com/recipe/absolute-best-ever-lasagna-28768")

# 1. Locate the main ingredient list container
try:
    ingredient_list = driver.find_element(By.CLASS_NAME, "ingredient-list")
    # Alternatively, use the full class if needed:
    # ingredient_list = driver.find_element(By.CSS_SELECTOR, ".ingredient-list.svelte-ik1ga1")
    
    # 2. Find all list items (li) inside the container
    ingredients = ingredient_list.find_elements(By.TAG_NAME, "li")
    
    print(f"{'Quantity':<10} | {'Unit/Context':<20} | {'Full Text'}")
    print("-" * 60)

    for item in ingredients:
        try:
            # Extract the raw quantity string
            qty_el = item.find_element(By.CLASS_NAME, "ingredient-quantity")
            quantity = qty_el.text.strip()
            
            # Extract the text description string
            text_el = item.find_element(By.CLASS_NAME, "ingredient-text")
            full_text = text_el.text.strip()
            
            # 3. Regex logic to capture the unit
            # This looks inside parentheses if they exist, or grabs the first word
            unit_match = re.search(r'^\((.*?)\)|^(\w+)', full_text)
            
            unit = ""
            if unit_match:
                # Group 1 handles parentheses like "(16 ounce) can" -> "16 ounce"
                # Group 2 handles normal first words like "teaspoon salt" -> "teaspoon"
                unit = unit_match.group(1) if unit_match.group(1) else unit_match.group(2)
            
    
            
            print(f"{quantity:<10} | {unit:<20} | {full_text}")
            
        except Exception as e:
            # Handles empty list items or structure variations gracefully
            continue

finally:
    driver.quit()