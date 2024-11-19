"""
AI-Powered Shopping Tool - Search Tests
----------------------------------------------------------------------------- 
Test suite for search and recommendation functionality.
----------------------------------------------------------------------------- 

Version History:
---------------
[Version history prior to v1.0 can be found in version_history.txt]

v1.0 - 11/19/24 - Jakub Bartkowiak
    - First stable release with comprehensive test suite
    - Terminal-based search interface
    - Result section limiting
    - Category-based result grouping

v1.1 - 11/19/24 - Jakub Bartkowiak
    - Updated to use centralized database configuration
    - Added proper session management
    - Enhanced error handling
    - Improved test coverage
"""

from search import search_products, suggest_products_for_item
from models import Product, Session, initialize_database_config
from contextlib import contextmanager
import sys

# Initialize database configuration
DATABASE_URI = initialize_database_config()

@contextmanager
def get_session():
    """Context manager for handling database sessions"""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

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
