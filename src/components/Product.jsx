import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FavoriteBorderOutlined,
  SearchOutlined,
  ShoppingCartOutlined,
  Star,
  StarBorder,
} from "@material-ui/icons";
import styled from "styled-components";
import { cartService } from "../data";

const Container = styled.div`
  flex: 1;
  margin: 5px;
  min-width: 280px;
  height: 400px;
  display: flex;
  flex-direction: column;
  background-color: #f5fbfd;
  position: relative;
`;

const ImageContainer = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
`;

const Info = styled.div`
  opacity: 0;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.5s ease;
  cursor: pointer;
`;

const Circle = styled.div`
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background-color: white;
  position: absolute;
`;

const Image = styled.img`
  height: 75%;
  z-index: 2;
  object-fit: cover;
`;

const Icon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 10px;
  transition: all 0.5s ease;
  cursor: pointer;

  &:hover {
    background-color: #e9f5f5;
    transform: scale(1.1);
  }
`;

const Details = styled.div`
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const Title = styled.h3`
  font-size: 16px;
  margin: 0;
  color: #2c2c2c;
`;

const Price = styled.span`
  font-weight: bold;
  font-size: 18px;
  color: #333;
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 2px;
`;

const StarIcon = styled(Star)`
  color: #ffc107;
  font-size: 18px !important;
`;

const StarBorderIcon = styled(StarBorder)`
  color: #ffc107;
  font-size: 18px !important;
`;

const Category = styled.span`
  font-size: 14px;
  color: #666;
  text-transform: capitalize;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4;
`;

const Product = ({ item }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleAddToCart = async (e) => {
    e.stopPropagation();
    try {
      setLoading(true);
      await cartService.addToCart(item.id);
      // Could add a toast notification here
    } catch (error) {
      console.error("Error adding to cart:", error);
      // Could add error notification here
    } finally {
      setLoading(false);
    }
  };

  const handleProductClick = () => {
    navigate(`/product/${item.id}`);
  };

  const handleSearchClick = (e) => {
    e.stopPropagation();
    navigate(`/product/${item.id}`);
  };

  const renderRating = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<StarIcon key={i} />);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<StarIcon key={i} style={{ clipPath: "inset(0 50% 0 0)" }} />);
      } else {
        stars.push(<StarBorderIcon key={i} />);
      }
    }
    return stars;
  };

  return (
    <Container onClick={handleProductClick}>
      <ImageContainer>
        <Circle />
        <Image src={item.img} alt={item.title} />
        <Info>
          <Icon onClick={handleAddToCart}>
            <ShoppingCartOutlined />
          </Icon>
          <Icon onClick={handleSearchClick}>
            <SearchOutlined />
          </Icon>
          <Icon>
            <FavoriteBorderOutlined />
          </Icon>
        </Info>
        {loading && (
          <LoadingOverlay>
            Adding to cart...
          </LoadingOverlay>
        )}
      </ImageContainer>
      <Details>
        <Title>{item.title}</Title>
        <Category>{item.category}</Category>
        <Rating>{renderRating(item.ratings)}</Rating>
        <Price>${item.price.toFixed(2)}</Price>
      </Details>
    </Container>
  );
};

export default Product;
