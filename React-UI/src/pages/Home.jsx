import React, { useState } from "react";
import Announcement from "../components/Announcement";
import Categories from "../components/Categories";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import Newsletter from "../components/Newsletter";
import Products from "../components/Products";
import Slider from "../components/Slider";
import Cart from "./Cart";
import Login from "./Login";
import ProductList from "./ProductList";
import Register from "./Register";

const Home = () => {
  const [activeShoppingCart, setActiveShoppingCart] = useState(false);
  const [activeProductsPage, setactiveProductsPage] = useState(false);
  const [activeRegistration, setActiveRegistration] = useState(false);
  const [activeSignin, setActiveSignin] = useState(false);
  const [pageName, setPageName] = useState('Home');

  // Function to reset to Home
  const goToHome = () => {
    setPageName('Home');
    setActiveShoppingCart(false);
    setactiveProductsPage(false);
    setActiveRegistration(false);
    setActiveSignin(false);
  };

  // Function to toggle the registration modal
  const changeRegState = () => {
    setActiveRegistration(!activeRegistration);
    if (!activeRegistration) {
      setActiveSignin(false);
      setActiveShoppingCart(false);
      setactiveProductsPage(false);
    }
  };

  // Function to toggle the shopping cart modal
  const toggleShoppingCart = () => {
    setActiveShoppingCart(!activeShoppingCart);
    if (!activeShoppingCart) {
      setActiveRegistration(false);
      setActiveSignin(false);
      setactiveProductsPage(false);
    }
  };

  // Function to toggle the products page modal
  const toggleProductsPage = () => {
    setactiveProductsPage(!activeProductsPage);
    if (!activeProductsPage) {
      setActiveRegistration(false);
      setActiveSignin(false);
      setActiveShoppingCart(false);
    }
  };

  // Function to toggle the sign-in modal
  const toggleSignin = () => {
    setActiveSignin(!activeSignin);
    if (!activeSignin) {
      setActiveRegistration(false);
      setActiveShoppingCart(false);
      setactiveProductsPage(false);
    }
  };

  return (
    <div>
      <Announcement />
      <Navbar 
        changeRegState={changeRegState}
        toggleShoppingCart={toggleShoppingCart}
        toggleSignin={toggleSignin}
        toggleProductsPage={toggleProductsPage}
        goToHome={goToHome} // pass the function to Navbar
      />
      
      {/* Home Button - will trigger the goToHome function */}
      <button onClick={goToHome} style={{ position: 'fixed', top: '20px', left: '20px' }}>
        Home
      </button>

      {/* Display different content based on the active state */}
      {(!activeShoppingCart && !activeRegistration && !activeSignin && !activeProductsPage) ? (
        <>
          <Slider />
          <Categories />
          <Products />
          <Newsletter />
          <Footer />
        </>
      ) : (!activeShoppingCart && !activeRegistration && !activeProductsPage && activeSignin) ? (
        <Login/>
      ) : (!activeShoppingCart && activeRegistration && !activeProductsPage && !activeSignin) ? (
        <Register/>
      ) : (activeShoppingCart && !activeRegistration && !activeProductsPage && !activeSignin) ? (
        <Cart/>
      ) : (!activeShoppingCart && !activeRegistration && activeProductsPage && !activeSignin) ? (
        <ProductList/>
      ) : null}
    </div>
  );
};

export default Home;
