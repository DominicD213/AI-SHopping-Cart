import { Add, Remove } from "@material-ui/icons";
import styled from "styled-components";
import { useState, useEffect } from "react";
import Footer from "../components/Footer";
import { mobile } from "../responsive";
import axios from "axios"; // Import axios for API calls

const Container = styled.div``;
// ...other styled components...

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch initial cart items from the backend or localStorage
    // For simplicity, we'll use a dummy initial state here
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

  // Function to add to cart and log activity to the backend
  const handleAddToCart = async (item) => {
    try {
      await axios.post(`/api/cart/add/${item.id}`); // Connect to the add to cart API
      console.log("Item added to cart and logged successfully.");
    } catch (error) {
      console.error("Failed to add item to cart", error);
    }
  };

  // Function to handle purchase
  const handlePurchase = async () => {
    const productIds = cartItems.map(item => item.id); // Extract product IDs
    try {
      await axios.post('/api/purchase', { product_ids: productIds });
      console.log("Purchase logged successfully.");
      // Clear cart after purchase (optional)
      setCartItems([]);
    } catch (error) {
      console.error("Failed to log purchase", error);
    }
  };

  // Calculate subtotal
  const subtotal = cartItems.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0
  );

  if (loading) return <div>Loading...</div>; // Add a loading state if needed

  return (
    <Container>
      <Wrapper>
        <Title>YOUR BAG</Title>
        <Top>
          <TopButton onClick={() => handlePurchase()}>CHECKOUT NOW</TopButton>
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
                    <Add onClick={() => { handleIncreaseQuantity(item.id); handleAddToCart(item); }} />
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
          </Summary>
        </Bottom>
      </Wrapper>
      <Footer />
    </Container>
  );
};

export default Cart;
