import styled from "styled-components";
import { mobile } from "../responsive";
import { useState } from "react";

const Container = styled.div`
  width: 100vw;
  height: 100vh;
  background: linear-gradient(
      rgba(255, 255, 255, 0.5),
      rgba(255, 255, 255, 0.5)
    ),
    url("https://images.pexels.com/photos/6984661/pexels-photo-6984661.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940")
      center;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Wrapper = styled.div`
  width: 40%;
  padding: 20px;
  background-color: white;
  ${mobile({ width: "75%" })}
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 300;
`;

const Form = styled.form`
  display: flex;
  flex-wrap: wrap;
`;

const Input = styled.input`
  flex: 1;
  min-width: 40%;
  margin: 20px 10px 0px 0px;
  padding: 10px;
`;

const Agreement = styled.span`
  font-size: 12px;
  margin: 20px 0px;
`;

const Button = styled.button`
  width: 40%;
  border: none;
  padding: 15px 20px;
  background-color: teal;
  color: white;
  cursor: pointer;
`;

const Register = () => {
  const [userData, setUserData] = useState({
    name: "",
    lastName: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    setUserData({ ...userData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    
    if (userData.password !== userData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });
      
      const result = await response.json();

      if (response.ok) {
        // Redirect to login page after successful registration
        window.location.href = "/login";
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError("An error occurred during registration");
    }
  };

  return (
    <Container>
      <Wrapper>
        <Title>CREATE AN ACCOUNT</Title>
        <Form onSubmit={handleRegister}>
          <Input
            name="name"
            placeholder="name"
            value={userData.name}
            onChange={handleInputChange}
          />
          <Input
            name="lastName"
            placeholder="last name"
            value={userData.lastName}
            onChange={handleInputChange}
          />
          <Input
            name="username"
            placeholder="username"
            value={userData.username}
            onChange={handleInputChange}
          />
          <Input
            name="email"
            placeholder="email"
            value={userData.email}
            onChange={handleInputChange}
          />
          <Input
            name="password"
            type="password"
            placeholder="password"
            value={userData.password}
            onChange={handleInputChange}
          />
          <Input
            name="confirmPassword"
            type="password"
            placeholder="confirm password"
            value={userData.confirmPassword}
            onChange={handleInputChange}
          />
          <Agreement>
            By creating an account, I consent to the processing of my personal
            data in accordance with the <b>PRIVACY POLICY</b>
          </Agreement>
          <Button type="submit">CREATE</Button>
          {error && <p>{error}</p>}
        </Form>
      </Wrapper>
    </Container>
  );
};

export default Register;
