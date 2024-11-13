import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Add, Remove } from "@material-ui/icons";
import styled from "styled-components";
import Footer from "../components/Footer";
import { mobile } from "../responsive";
import { cartService } from "../data";

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

const TopTexts = styled.div`
  ${mobile({ display: "none" })}
`;

const TopText = styled.span`
  text-decoration: underline;
  cursor: pointer;
  margin: 0px 10px;
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
  object-fit: cover;
`;

const Details = styled.div`
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
`;

const ProductName = styled.span`
  font-size: 16px;
  font-weight: 500;
`;

const ProductId = styled.span`
  color: #666;
`;

const ProductCategory = styled.span`
  color: #666;
  text-transform: capitalize;
`;

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
  margin: 15px 0;
`;

const Summary = styled.div`
  flex: 1;
  border: 0.5px solid lightgray;
  border-radius: 10px;
  padding: 20px;
  height: fit-content;
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
  cursor: pointer;
  &:disabled {
    background-color: #666;
    cursor: not-allowed;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 18px;
  color: #666;
`;

const ErrorContainer = styled.div`
  color: red;
  text-align: center;
  padding: 20px;
`;

const EmptyCartMessage = styled.div`
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
`;

const Cart = () => {
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      setLoading(true);
      setError(null);
      const items = await cartService.getCart();
      setCartItems(items);
    } catch (err) {
      setError("Failed to load cart. Please try again later.");
      console.error("Error fetching cart:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = async (productId, change) => {
    try {
      setUpdating(true);
      if (change > 0) {
        await cartService.addToCart(productId);
      } else {
        await cartService.removeFromCart(productId);
      }
      await fetchCart();
    } catch (err) {
      setError("Failed to update quantity. Please try again.");
      console.error("Error updating quantity:", err);
    } finally {
      setUpdating(false);
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  if (loading) {
    return (
      <Container>
        <LoadingContainer>Loading cart...</LoadingContainer>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <ErrorContainer>{error}</ErrorContainer>
      </Container>
    );
  }

  return (
    <Container>
      <Wrapper>
        <Title>YOUR CART</Title>
        <Top>
          <TopButton onClick={() => navigate("/products")}>
            CONTINUE SHOPPING
          </TopButton>
          <TopTexts>
            <TopText>Shopping Cart ({cartItems.length})</TopText>
          </TopTexts>
          <TopButton 
            type="filled" 
            onClick={() => navigate("/checkout")}
            disabled={cartItems.length === 0}
          >
            CHECKOUT NOW
          </TopButton>
        </Top>
        <Bottom>
          <Info>
            {cartItems.length === 0 ? (
              <EmptyCartMessage>Your cart is empty</EmptyCartMessage>
            ) : (
              cartItems.map((item) => (
                <div key={item.product_id}>
                  <Product>
                    <ProductDetail>
                      <Image src={item.image_url || "https://via.placeholder.com/200"} />
                      <Details>
                        <ProductName>{item.title}</ProductName>
                        <ProductId>
                          <b>ID:</b> {item.product_id}
                        </ProductId>
                        <ProductCategory>
                          <b>Category:</b> {item.category}
                        </ProductCategory>
                      </Details>
                    </ProductDetail>
                    <PriceDetail>
                      <ProductAmountContainer>
                        <Remove 
                          style={{ cursor: "pointer" }}
                          onClick={() => handleQuantityChange(item.product_id, -1)}
                        />
                        <ProductAmount>{item.quantity}</ProductAmount>
                        <Add 
                          style={{ cursor: "pointer" }}
                          onClick={() => handleQuantityChange(item.product_id, 1)}
                        />
                      </ProductAmountContainer>
                      <ProductPrice>$ {(item.price * item.quantity).toFixed(2)}</ProductPrice>
                    </PriceDetail>
                  </Product>
                  <Hr />
                </div>
              ))
            )}
          </Info>
          <Summary>
            <SummaryTitle>ORDER SUMMARY</SummaryTitle>
            <SummaryItem>
              <SummaryItemText>Subtotal</SummaryItemText>
              <SummaryItemPrice>$ {calculateTotal().toFixed(2)}</SummaryItemPrice>
            </SummaryItem>
            <SummaryItem>
              <SummaryItemText>Estimated Shipping</SummaryItemText>
              <SummaryItemPrice>$ {cartItems.length > 0 ? "5.90" : "0.00"}</SummaryItemPrice>
            </SummaryItem>
            <SummaryItem>
              <SummaryItemText>Shipping Discount</SummaryItemText>
              <SummaryItemPrice>$ {cartItems.length > 0 ? "-5.90" : "0.00"}</SummaryItemPrice>
            </SummaryItem>
            <SummaryItem type="total">
              <SummaryItemText>Total</SummaryItemText>
              <SummaryItemPrice>$ {calculateTotal().toFixed(2)}</SummaryItemPrice>
            </SummaryItem>
            <Button 
              disabled={cartItems.length === 0 || updating}
              onClick={() => navigate("/checkout")}
            >
              CHECKOUT NOW
            </Button>
          </Summary>
        </Bottom>
      </Wrapper>
      <Footer />
    </Container>
  );
};

export default Cart;
