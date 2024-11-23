import React, { useState, useEffect } from "react";
import axios from "axios";
import { Add, Remove } from "@material-ui/icons";
import styled from "styled-components";
import Footer from "../components/Footer";
import CheckoutPage from "../components/checkout";
import Summary from "../components/summary";

// Styled Components
const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 90vh;
`;

const Container = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 20px;
  flex: 1; /* Make sure the main content fills the available space */
`;

const LeftContainer = styled.div`
  flex: 2;
  margin-right: 20px;
`;

const RightContainer = styled.div`
  flex: 1;
`;

const Title = styled.h1`
  font-weight: 300;
  text-align: center;
`;

const TopButton = styled.button`
  padding: 10px;
  font-weight: 600;
  cursor: pointer;
  background-color: ${(props) => (props.type === "filled" ? "black" : "transparent")};
  color: ${(props) => (props.type === "filled" ? "white" : "black")};
  border: ${(props) => (props.type === "filled" && "none")};
`;

const Product = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
`;

const ProductDetail = styled.div`
  flex: 2;
  display: flex;
`;

const Image = styled.img`
  width: 200px;
`;

const Details = styled.div`
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
`;

const ProductName = styled.span``;

const ProductId = styled.span``;

const ProductColor = styled.div`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: ${(props) => props.color};
`;

const ProductSize = styled.span``;

const PriceDetail = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const ProductAmountContainer = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 20px;
`;

const ProductAmount = styled.div`
  font-size: 24px;
  margin: 5px;
`;

const ProductPrice = styled.div`
  font-size: 30px;
  font-weight: 200;
`;

const Hr = styled.hr`
  background-color: #eee;
  border: none;
  height: 1px;
`;

const EmptyCartNotification = styled.div`
  font-size: 20px;
  color: red;
  text-align: center;
  margin-top: 20px;
`;

const RecommendationSection = styled.div`
  margin-top: 40px;
  padding: 20px;
  background-color: #f4f4f4;
  border-radius: 10px;
`;

const RecommendationTitle = styled.h2`
  text-align: center;
  font-weight: 300;
`;

const RecommendationItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
`;

const RecommendationItemName = styled.span`
  font-weight: 500;
`

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCheckout, setCheckout] = useState(false);
  const [recommendations, setRecommendations] = useState([]);

  // Fetch cart items from the backend API
  useEffect(() => {
    const fetchCartItems = async () => {
      try {
        const response = await axios.get("/api/cart");
        setCartItems(response.data.items); // Assuming API returns an object with an array of items
        setLoading(false);
      } catch (error) {
        console.error("Error fetching cart items:", error);
        setLoading(false);
      }
    };

    // Fetch recommendations from AI backend
    const fetchRecommendations = async () => {
      try {
        const response = await axios.get("/api/recommendations");
        setRecommendations(response.data.recommendations); // Assuming API returns recommended products
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      }
    };

    fetchCartItems();
    fetchRecommendations();
  }, []);

  // Increase quantity of an item in the cart
  const handleIncreaseQuantity = async (itemId) => {
    try {
      const response = await axios.patch(`/api/cart/${itemId}`, { quantity: 1 });
      setCartItems(response.data.items); // Update cart after quantity increase
    } catch (error) {
      console.error("Error increasing quantity:", error);
    }
  };

  // Decrease quantity of an item in the cart
  const handleDecreaseQuantity = async (itemId) => {
    try {
      const response = await axios.patch(`/api/cart/${itemId}`, { quantity: -1 });
      setCartItems(response.data.items); // Update cart after quantity decrease
    } catch (error) {
      console.error("Error decreasing quantity:", error);
    }
  };

  // Handle checkout and purchase
  const handlePurchase = async () => {
    setCheckout(true); // Transition to Checkout Page
    const productIds = cartItems.map((item) => item.id);

    try {
      await axios.post("/api/purchase", { product_ids: productIds });
      setCartItems([]); // Clear cart after purchase
    } catch (error) {
      console.error("Error processing purchase:", error);
    }
  };

  const subtotal = cartItems.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0
  );

  const displayTotalPrice = cartItems.length === 0 ? 0 : subtotal;

  return !isCheckout ? (
    <AppContainer>
      <Container>
        <LeftContainer>
          <Title>YOUR BAG</Title>
          {cartItems.length === 0 ? (
            <EmptyCartNotification>Your cart is empty!</EmptyCartNotification>
          ) : (
            cartItems.map((item) => (
              <Product key={item.id}>
                <ProductDetail>
                  <Image src={item.image} alt={item.name} />
                  <Details>
                    <ProductName>
                      <b>Product:</b> {item.name}
                    </ProductName>
                    <ProductId>
                      <b>ID:</b> {item.id}
                    </ProductId>
                    <ProductColor color={item.color} />
                    <ProductSize>
                      <b>Size:</b> {item.size}
                    </ProductSize>
                  </Details>
                </ProductDetail>
                <PriceDetail>
                  <ProductAmountContainer>
                    <Add onClick={() => handleIncreaseQuantity(item.id)} />
                    <ProductAmount>{item.quantity}</ProductAmount>
                    <Remove onClick={() => handleDecreaseQuantity(item.id)} />
                  </ProductAmountContainer>
                  <ProductPrice>${item.price * item.quantity}</ProductPrice>
                </PriceDetail>
              </Product>
            ))
          )}
          <Hr />
        </LeftContainer>
        <RightContainer>
          <Summary subtotal={displayTotalPrice} onCheckout={handlePurchase} />
          {cartItems.length > 0 && (
            <RecommendationSection>
              <RecommendationTitle>Recommended for You</RecommendationTitle>
              {recommendations.map((item) => (
                <RecommendationItem key={item.id}>
                  <RecommendationItemName>{item.name}</RecommendationItemName>
                  <span>${item.price}</span>
                </RecommendationItem>
              ))}
            </RecommendationSection>
          )}
        </RightContainer>
      </Container>
      <Footer />
    </AppContainer>
  ) : (
    <CheckoutPage cartItems={cartItems} subtotal={displayTotalPrice} onClick={handlePurchase} />
  );
};

export default Cart;