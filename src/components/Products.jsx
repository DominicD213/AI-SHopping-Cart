import { useState, useEffect } from "react";
import styled from "styled-components";
import { productService } from "../data";
import Product from "./Product";

const Container = styled.div`
    padding: 20px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
`;

const LoadingContainer = styled.div`
    width: 100%;
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 18px;
    color: #666;
`;

const ErrorContainer = styled.div`
    width: 100%;
    padding: 20px;
    text-align: center;
    color: #ff4444;
`;

const Products = ({ category, filters, sort }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Prepare search filters
        const searchFilters = {
          category: category,
          ...filters,
          sort_by: sort
        };
        
        // Fetch products using our API service
        const data = await productService.getProducts(searchFilters);
        
        // Transform the data to match our component needs
        const transformedProducts = data.map(product => ({
          id: product.product_id,
          title: product.title,
          price: product.price,
          category: product.category,
          ratings: product.ratings,
          img: product.image_url || "https://via.placeholder.com/200", // Fallback image
          brand: product.brand,
          description: product.description
        }));
        
        setProducts(transformedProducts);
      } catch (err) {
        setError("Failed to load products. Please try again later.");
        console.error("Error fetching products:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [category, filters, sort]);

  if (loading) {
    return (
      <LoadingContainer>
        Loading products...
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ErrorContainer>
        {error}
      </ErrorContainer>
    );
  }

  if (products.length === 0) {
    return (
      <Container>
        <ErrorContainer>
          No products found matching your criteria.
        </ErrorContainer>
      </Container>
    );
  }

  return (
    <Container>
      {products.map((item) => (
        <Product item={item} key={item.id} />
      ))}
    </Container>
  );
};

export default Products;
