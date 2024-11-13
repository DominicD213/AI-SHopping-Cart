import React, { useState } from "react";
import styled from "styled-components";
import axios from "axios";

// Styled components
const Container = styled.div`
  padding: 20px;
`;

const Title = styled.h1`
  font-weight: 300;
  text-align: center;
`;

const Wrapper = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
`;

const Summary = styled.div`
  width: 45%;
  border: 0.5px solid lightgray;
  border-radius: 10px;
  padding: 20px;
`;

const SummaryItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  font-weight: ${(props) => props.type === "total" && "500"};
`;

const SummaryItemText = styled.span``;

const SummaryItemPrice = styled.span``;

const CheckoutForm = styled.form`
  width: 45%;
  border: 0.5px solid lightgray;
  border-radius: 10px;
  padding: 20px;
`;

const FormLabel = styled.label`
  margin-bottom: 5px;
  font-weight: 600;
`;

const FormInput = styled.input`
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  font-size: 16px;
  border: 1px solid lightgray;
  border-radius: 5px;
`;

const CreditCardForm = styled.div`
  margin-top: 20px;
  display: ${props => props.show ? 'block' : 'none'};
`;

const CreditCardInput = styled.input`
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  font-size: 16px;
  border: 1px solid lightgray;
  border-radius: 5px;
`;

const Button = styled.button`
  width: 100%;
  padding: 10px;
  background-color: black;
  color: white;
  font-weight: 600;
  cursor: pointer;
`;

const ItemList = styled.div`
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
`;

const Item = styled.div`
  display: flex;
  margin-bottom: 15px;
  border-bottom: 1px solid lightgray;
  padding-bottom: 10px;
`;

const ItemImage = styled.img`
  width: 60px;
  height: 60px;
  object-fit: cover;
  margin-right: 20px;
`;

const ItemDetails = styled.div`
  flex-grow: 1;
`;

const ItemName = styled.div`
  font-weight: 600;
`;

const ItemSize = styled.div`
  font-size: 14px;
  color: gray;
`;

const ItemPrice = styled.div`
  font-weight: bold;
  color: #333;
`;

const CheckoutPage = ({ cartItems, subtotal }) => {
  const [customerDetails, setCustomerDetails] = useState({
    name: "",
    email: "",
    address: "",
    city: "",
    zip: "",
  });

  const [showCreditCardForm, setShowCreditCardForm] = useState(false);
  const [creditCard, setCreditCard] = useState({
    cardNumber: "",
    expiryDate: "",
    cvv: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCustomerDetails((prevDetails) => ({
      ...prevDetails,
      [name]: value,
    }));
  };

  const handleCreditCardChange = (e) => {
    const { name, value } = e.target;
    setCreditCard((prevCard) => ({
      ...prevCard,
      [name]: value,
    }));
  };

  const handlePurchase = async (e) => {
    e.preventDefault();
    if (!customerDetails.name || !customerDetails.email || !customerDetails.address) {
      alert("Please complete all fields.");
      return;
    }

    setShowCreditCardForm(true);
  };

  const handleSubmitPurchase = async (e) => {
    e.preventDefault();
    if (!creditCard.cardNumber || !creditCard.expiryDate || !creditCard.cvv) {
      alert("Please complete the credit card details.");
      return;
    }

    try {
      await axios.post("/api/checkout", {
        customer: customerDetails,
        products: cartItems.map((item) => item.id),
        creditCard: creditCard, // Sending credit card info
      });
      alert("Purchase successful!");
    } catch (error) {
      console.error("Purchase failed", error);
      alert("Purchase failed. Please try again.");
    }
  };

  const shipping = 5.9;
  const total = subtotal + shipping;

  return (
    <Container>
      <Title>Checkout</Title>

      {/* Side-by-side Layout */}
      <Wrapper>
        {/* Order Summary */}
        <Summary>
          <SummaryItem>
            <SummaryItemText>Subtotal</SummaryItemText>
            <SummaryItemPrice>${subtotal}</SummaryItemPrice>
          </SummaryItem>
          <SummaryItem>
            <SummaryItemText>Shipping</SummaryItemText>
            <SummaryItemPrice>${shipping}</SummaryItemPrice>
          </SummaryItem>
          <SummaryItem type="total">
            <SummaryItemText>Total</SummaryItemText>
            <SummaryItemPrice>${total}</SummaryItemPrice>
          </SummaryItem>

          {/* Cart Items Display */}
          <ItemList>
            {cartItems.map((item) => (
              <Item key={item.id}>
                <ItemImage src={item.image} alt={item.name} />
                <ItemDetails>
                  <ItemName>{item.name}</ItemName>
                  <ItemSize>Size: {item.size}</ItemSize>
                  <ItemPrice>${item.price} x {item.quantity}</ItemPrice>
                </ItemDetails>
              </Item>
            ))}
          </ItemList>
        </Summary>

        {/* Checkout Form */}
        <CheckoutForm onSubmit={handlePurchase}>
          <FormLabel>Name</FormLabel>
          <FormInput
            name="name"
            value={customerDetails.name}
            onChange={handleInputChange}
          />
          <FormLabel>Email</FormLabel>
          <FormInput
            name="email"
            value={customerDetails.email}
            onChange={handleInputChange}
          />
          <FormLabel>Address</FormLabel>
          <FormInput
            name="address"
            value={customerDetails.address}
            onChange={handleInputChange}
          />
          <FormLabel>City</FormLabel>
          <FormInput
            name="city"
            value={customerDetails.city}
            onChange={handleInputChange}
          />
          <FormLabel>ZIP Code</FormLabel>
          <FormInput
            name="zip"
            value={customerDetails.zip}
            onChange={handleInputChange}
          />
          <Button type="submit">Complete Purchase</Button>
        </CheckoutForm>
      </Wrapper>

      {/* Credit Card Form (shows after clicking "Complete Purchase") */}
      <CreditCardForm show={showCreditCardForm}>
        <Title>Enter Credit Card Information</Title>
        <FormLabel>Card Number</FormLabel>
        <CreditCardInput
          name="cardNumber"
          value={creditCard.cardNumber}
          onChange={handleCreditCardChange}
        />
        <FormLabel>Expiry Date</FormLabel>
        <CreditCardInput
          name="expiryDate"
          value={creditCard.expiryDate}
          onChange={handleCreditCardChange}
        />
        <FormLabel>CVV</FormLabel>
        <CreditCardInput
          name="cvv"
          value={creditCard.cvv}
          onChange={handleCreditCardChange}
        />
        <Button onClick={handleSubmitPurchase}>Submit Payment</Button>
      </CreditCardForm>
    </Container>
  );
};

export default CheckoutPage;
