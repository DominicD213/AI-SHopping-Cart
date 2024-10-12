import React from "react";
import Announcement from "../components/Announcement";
import Categories from "../components/Categories";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import Newsletter from "../components/Newsletter";
import Products from "../components/Products";
import Slider from "../components/Slider";
import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import Cart from "./Cart"

const Home = () => {
  const [activeShoppingCart, setActiveShoppingCart] = useState(false);
  const [activeRegistration, setActiveRegistration] = useState(false);
  const [activeSignin, setActiveSignin] = useState(false);

  // Function to toggle the registration modal
  const changeRegState = () => {
    setActiveRegistration(!activeRegistration);
  };

  // Function to toggle the shopping cart modal
  const toggleShoppingCart = () => {
    setActiveShoppingCart(!activeShoppingCart);
  };

  // Function to toggle the sign-in modal
  const toggleSignin = () => {
    setActiveSignin(!activeSignin);
  };

  return (
    <div>
      <Announcement />
      <Navbar 
        changeRegState={changeRegState}
        toggleShoppingCart={toggleShoppingCart}
        toggleSignin={toggleSignin}
      />
     {(!activeShoppingCart && !activeRegistration && !activeSignin) ? (
      <>
      <Slider />
      <Categories />
      <Products />
      <Newsletter />
      <Footer />
      </>
    ) : 
    (!activeShoppingCart && !activeRegistration && activeSignin)? (
      <Login/>
    ):
    (!activeShoppingCart && activeRegistration && !activeSignin)? (
      <Register/>
    ):
    (activeShoppingCart && !activeRegistration && !activeSignin)? (
      <Cart/>
    ): null
    }
    </div>
  );
};

export default Home;