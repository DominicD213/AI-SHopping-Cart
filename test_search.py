"""
AI-Powered Shopping Tool - Search Tests
----------------------------------------------------------------------------- 
Test suite for search and recommendation functionality.
----------------------------------------------------------------------------- 

Version History:
---------------
[please please remember to add your name, date, and version number if you change anything, even when using Github  - thanks, JB]
---------------

100%, 3/3


v0.1- 11/14/24 - Jakub Bartkowiak
    - Initial personal testing implementation for basic search functionality and database interaction

v0.2-0.3 - 11/15-11/16/24 - Jakub Bartkowiak
    - Generalized code for simplicity and to allow for use  by other team members
    - Added terminal-based search interface
    - Implemented result section limiting
"""

from search import search_products, suggest_products_for_item
from data.import_data import add_product, Session
from models import Product
import sys

def print_results(results, section_name="Results", limit=5):
    """Print formatted search results"""
    if not results:
        print(f"\nNo {section_name.lower()} found.")
        return
        
    print(f"\n{section_name}:")
    print("-" * len(section_name))
    
    # Only show up to limit results
    for result in results[:limit]:
        print(f"Product: {result['title']}")
        print(f"Price: ${result['price']:.2f}")
        if result.get('was_price'):
            print(f"Was: ${result['was_price']:.2f}")
        if result.get('discount'):
            print(f"Discount: {result['discount']}%")
        print()

def terminal_search():
    """Handle terminal-based product search"""
    session = Session()
    
    while True:
        try:
            # Get search query from terminal
            query = input("\nEnter search term (or 'exit' to quit): ").strip()
            
            if query.lower() == 'exit':
                print("\nExiting search...")
                break
                
            if not query:
                print("\nPlease enter a search term.")
                continue
            
            # Perform search
            results = search_products(query, simple_mode=True)
            
            if not results:
                print("\nNo products found matching your search.")
                continue
            
            # Group results by category
            categorized_results = {}
            for result in results:
                category = result['category'] or 'Uncategorized'
                if category not in categorized_results:
                    categorized_results[category] = []
                categorized_results[category].append(result)
            
            # Print results by category, limited to 5 per category
            for category, items in categorized_results.items():
                print_results(items, f"{category} Products", limit=5)
                
        except KeyboardInterrupt:
            print("\n\nSearch interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nError during search: {str(e)}")
            continue

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Run original test suite
        test_search()
        test_recommendations()
    else:
        # Run terminal search interface
        terminal_search()
