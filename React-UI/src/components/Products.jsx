import styled from "styled-components";
import { useEffect, useState } from "react";
import Product from "./Product";
import axios from "axios"; // Import Axios for API calls

const Container = styled.div`
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
`;

const Products = () => {
  const [products, setProducts] = useState([]); // State to store products
  const [error, setError] = useState(null); // State to handle errors

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/api/products");
        setProducts(response.data); // Assuming the API response is an array of products
      } catch (err) {
        setError("Failed to fetch products. Please try again later.");
      }
    };

    fetchProducts();
  }, []); // Empty dependency array ensures it runs once on mount

  if (error) {
    return <div>{error}</div>; // Display error message if API call fails
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
