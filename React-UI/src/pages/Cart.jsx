import { Add, Remove } from "@material-ui/icons";
import styled from "styled-components";
import { useState } from "react";
import Footer from "../components/Footer";
import { mobile } from "../responsive";

const Container = styled.div``;
// ...other styled components...

const Cart = () => {
  // Initial cart items
  const [cartItems, setCartItems] = useState([
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

  // Function to handle incrementing item quantity
  const handleIncreaseQuantity = (itemId) => {
    setCartItems((prevItems) =>
      prevItems.map((item) =>
        item.id === itemId
          ? { ...item, quantity: item.quantity + 1 }
          : item
      )
    );
  };

  // Function to handle decrementing item quantity
  const handleDecreaseQuantity = (itemId) => {
    setCartItems((prevItems) =>
      prevItems.map((item) =>
        item.id === itemId && item.quantity > 1
          ? { ...item, quantity: item.quantity - 1 }
          : item
      )
    );
  };

  // Calculate subtotal
  const subtotal = cartItems.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0
  );

  return (
    <Container>
      <Wrapper>
        <Title>YOUR BAG</Title>
        <Top>
          <TopButton>CONTINUE SHOPPING</TopButton>
          <TopTexts>
            <TopText>Shopping Bag({cartItems.length})</TopText>
            <TopText>Your Wishlist (0)</TopText>
          </TopTexts>
          <TopButton type="filled">CHECKOUT NOW</TopButton>
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
            <Button>CHECKOUT NOW</Button>
          </Summary>
        </Bottom>
      </Wrapper>
      <Footer />
    </Container>
  );
};

export default Cart;
