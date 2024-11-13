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

  // Function to toggle the registration modal
  const changeRegState = () => {
    setActiveRegistration(!activeRegistration);
    if(activeSignin){
      setActiveSignin(!activeSignin)
    }
  };

  // Function to toggle the shopping cart modal
  const toggleShoppingCart = () => {
    setActiveShoppingCart(!activeShoppingCart);
  };

  // Function to toggle the products page modal
  const toggleProductsPage = () => {
    setactiveProductsPage(!activeProductsPage);
  };


  // Function to toggle the sign-in modal
  const toggleSignin = () => {
    setActiveSignin(!activeSignin);
    if(activeRegistration){
      setActiveRegistration(!activeRegistration);
    }
  };
  // Function to toggle the sign-in modal
  const togglePageName = (item) => {
    setPageName = item;
  };

  return (
    <div>
      <Announcement />
      <Navbar 
        changeRegState={changeRegState}
        toggleShoppingCart={toggleShoppingCart}
        toggleSignin={toggleSignin}
        toggleProductsPage ={toggleProductsPage}
        togglePageName ={togglePageName}
      />
     {(!activeShoppingCart && !activeRegistration && !activeSignin && !activeProductsPage) ? (
      <>
      <Slider />
      <Categories />
      <Products />
      <Newsletter />
      <Footer />
      </>
    ) : 
    (!activeShoppingCart && !activeRegistration && !activeProductsPage && activeSignin)? (
      <Login/>
    ):
    (!activeShoppingCart && activeRegistration && !activeProductsPage && !activeSignin)? (
      <Register/>
    ):
    (activeShoppingCart && !activeRegistration && !activeProductsPage && !activeSignin)? (
      <Cart/>
    ): (!activeShoppingCart && !activeRegistration && activeProductsPage && !activeSignin)? (
      <ProductList/>
    ):
    null
    }
    </div>
  );
};

export default Home;