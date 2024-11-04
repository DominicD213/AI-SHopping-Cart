// Cart.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import ChatPopup from "../components/chatPopup";
import { Add, Remove } from "@material-ui/icons";
import styled from "styled-components";
import Footer from "../components/Footer";
import { mobile } from "../responsive"; // Responsive design utilities

// Styled Components
const Container = styled.div``;

const Wrapper = styled.div`
    padding: 20px;
    ${mobile({ padding: "10px" })}
`;

const Title = styled.h1`
    font-weight: 300;
    text-align: center;
`;

const Top = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px;
`;

const TopButton = styled.button`
    padding: 10px;
    font-weight: 600;
    cursor: pointer;
    border: ${(props) => props.type === "filled" && "none"};
    background-color: ${(props) =>
        props.type === "filled" ? "black" : "transparent"};
    color: ${(props) => props.type === "filled" && "white"};
`;

const Bottom = styled.div`
    display: flex;
    justify-content: space-between;
    ${mobile({ flexDirection: "column" })}
`;

const Info = styled.div`
    flex: 3;
`;

const Product = styled.div`
    display: flex;
    justify-content: space-between;
    ${mobile({ flexDirection: "column" })}
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
    ${mobile({ margin: "5px 15px" })}
`;

const ProductPrice = styled.div`
    font-size: 30px;
    font-weight: 200;
    ${mobile({ marginBottom: "20px" })}
`;

const Hr = styled.hr`
    background-color: #eee;
    border: none;
    height: 1px;
`;

const Summary = styled.div`
    flex: 1;
    border: 0.5px solid lightgray;
    border-radius: 10px;
    padding: 20px;
    height: 50vh;
`;

const SummaryTitle = styled.h1`
    font-weight: 200;
`;

const SummaryItem = styled.div`
    margin: 30px 0px;
    display: flex;
    justify-content: space-between;
    font-weight: ${(props) => props.type === "total" && "500"};
    font-size: ${(props) => props.type === "total" && "24px"};
`;

const SummaryItemText = styled.span``;

const SummaryItemPrice = styled.span``;

const Button = styled.button`
    width: 100%;
    padding: 10px;
    background-color: black;
    color: white;
    font-weight: 600;
`;

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isChatOpen, setChatOpen] = useState(false); // State to manage chat visibility

  useEffect(() => {
      // Fetch initial cart items
      setCartItems([
          {
              id: 1,
              name: "JESSIE THUNDER SHOES",
              color: "black",
              size: "37.5",
              price: 30,
              quantity: 2,
              image: "https://hips.hearstapps.com/vader-prod.s3.amazonaws.com/1614188818-TD1MTHU_SHOE_ANGLE_GLOBAL_MENS_TREE_DASHERS_THUNDER_b01b1013-cd8d-48e7-bed9-52db26515dc4.png?crop=1xw:1.00xh;center,top&resize=480%3A%2A",
          },
          {
              id: 2,
              name: "HAKURA T-SHIRT",
              color: "gray",
              size: "M",
              price: 20,
              quantity: 1,
              image: "https://i.pinimg.com/originals/2d/af/f8/2daff8e0823e51dd752704a47d5b795c.png",
          },
      ]);
      setLoading(false);
  }, []);

  const handleIncreaseQuantity = (itemId) => {
      setCartItems((prevItems) =>
          prevItems.map((item) =>
              item.id === itemId
                  ? { ...item, quantity: item.quantity + 1 }
                  : item
          )
      );
  };

  const handleDecreaseQuantity = (itemId) => {
      setCartItems((prevItems) =>
          prevItems.map((item) =>
              item.id === itemId && item.quantity > 1
                  ? { ...item, quantity: item.quantity - 1 }
                  : item
          )
      );
  };

  const handlePurchase = async () => {
      const productIds = cartItems.map(item => item.id);
      try {
          await axios.post('/api/purchase', { product_ids: productIds });
          console.log("Purchase logged successfully.");
          setCartItems([]);
      } catch (error) {
          console.error("Failed to log purchase", error);
      }
  };

  const subtotal = cartItems.reduce(
      (acc, item) => acc + item.price * item.quantity,
      0
  );

  const toggleChat = () => {
      setChatOpen((prev) => !prev);
  };

  if (loading) return <div>Loading...</div>;

  return (
      <Container>
          <Wrapper>
              <Title>YOUR BAG</Title>
              <Top>
                  <TopButton onClick={handlePurchase}>CHECKOUT NOW</TopButton>
              </Top>
              <Bottom>
                  <Info>
                      {cartItems.map((item) => (
                          <Product key={item.id}>
                              <ProductDetail>
                                  <Image src={item.image} />
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
                      ))}
                      <Hr />
                  </Info>
                  <Summary>
                      <SummaryTitle>ORDER SUMMARY</SummaryTitle>
                      <SummaryItem>
                          <SummaryItemText>Subtotal</SummaryItemText>
                          <SummaryItemPrice>${subtotal}</SummaryItemPrice>
                      </SummaryItem>
                      <SummaryItem>
                          <SummaryItemText>Estimated Shipping</SummaryItemText>
                          <SummaryItemPrice>$5.90</SummaryItemPrice>
                      </SummaryItem>
                      <SummaryItem>
                          <SummaryItemText>Shipping Discount</SummaryItemText>
                          <SummaryItemPrice>$-5.90</SummaryItemPrice>
                      </SummaryItem>
                      <SummaryItem type="total">
                          <SummaryItemText>Total</SummaryItemText>
                          <SummaryItemPrice>${subtotal}</SummaryItemPrice>
                      </SummaryItem>
                      <Button onClick={handlePurchase}>CHECKOUT NOW</Button>
                      
                      {/* Chat Popup and Chat Button */}
                      <ChatPopup isOpen={isChatOpen} toggleChat={toggleChat} />
                      
                      {!isChatOpen && (
                          <button
                              onClick={toggleChat}
                              style={{
                                  position:"absolute",
                                  right: "5rem",
                                  marginTop:"5rem",
                                  padding: "10px 20px",
                                  backgroundColor: "black",
                                  color: "white",
                                  border: "none",
                                  boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                                  cursor: "pointer",
                                  zIndex: 1000
                              }}
                          >
                              Chat
                          </button>
                      )}
                  </Summary>
              </Bottom>
          </Wrapper>
          <Footer />
      </Container>
  );
};

export default Cart;
