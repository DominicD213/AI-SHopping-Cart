import { useState, useEffect } from "react";
import { useLocation, useSearchParams } from "react-router-dom";
import styled from "styled-components";
import Footer from "../components/Footer";
import Newsletter from "../components/Newsletter";
import Products from "../components/Products";
import { mobile } from "../responsive";
import { SYNONYM_MAP } from "../data";

const Container = styled.div``;

const Title = styled.h1`
  margin: 20px;
  text-transform: capitalize;
`;

const FilterContainer = styled.div`
  display: flex;
  justify-content: space-between;
`;

const Filter = styled.div`
  margin: 20px;
  ${mobile({ width: "0px 20px", display: "flex", flexDirection: "column" })}
`;

const FilterText = styled.span`
  font-size: 20px;
  font-weight: 600;
  margin-right: 20px;
  ${mobile({ marginRight: "0px" })}
`;

const Select = styled.select`
  padding: 10px;
  margin-right: 20px;
  ${mobile({ margin: "10px 0px" })}
`;

const Option = styled.option``;

const ProductList = () => {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Get category from URL path
  const category = location.pathname.split("/")[2];
  
  // States for filters and sort
  const [filters, setFilters] = useState({
    minPrice: searchParams.get("minPrice") || "",
    maxPrice: searchParams.get("maxPrice") || "",
    brand: searchParams.get("brand") || "",
    minRating: searchParams.get("minRating") || ""
  });
  
  const [sort, setSort] = useState(searchParams.get("sort") || "newest");

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    if (sort !== "newest") params.set("sort", sort);
    setSearchParams(params);
  }, [filters, sort, setSearchParams]);

  const handleFilters = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSort = (e) => {
    setSort(e.target.value);
  };

  // Get category title for display
  const getCategoryTitle = () => {
    if (!category) return "All Products";
    return category.charAt(0).toUpperCase() + category.slice(1);
  };

  return (
    <Container>
      <Title>{getCategoryTitle()}</Title>
      <FilterContainer>
        <Filter>
          <FilterText>Filter Products:</FilterText>
          <Select name="minRating" value={filters.minRating} onChange={handleFilters}>
            <Option value="">Rating (All)</Option>
            <Option value="4">4+ Stars</Option>
            <Option value="3">3+ Stars</Option>
            <Option value="2">2+ Stars</Option>
          </Select>
          <Select name="minPrice" value={filters.minPrice} onChange={handleFilters}>
            <Option value="">Min Price</Option>
            <Option value="25">$25</Option>
            <Option value="50">$50</Option>
            <Option value="100">$100</Option>
            <Option value="200">$200</Option>
          </Select>
          <Select name="maxPrice" value={filters.maxPrice} onChange={handleFilters}>
            <Option value="">Max Price</Option>
            <Option value="50">$50</Option>
            <Option value="100">$100</Option>
            <Option value="200">$200</Option>
            <Option value="500">$500</Option>
          </Select>
        </Filter>
        <Filter>
          <FilterText>Sort Products:</FilterText>
          <Select value={sort} onChange={handleSort}>
            <Option value="newest">Newest</Option>
            <Option value="price_asc">Price (Low to High)</Option>
            <Option value="price_desc">Price (High to Low)</Option>
            <Option value="rating_desc">Highest Rated</Option>
            <Option value="popularity_desc">Most Popular</Option>
          </Select>
        </Filter>
      </FilterContainer>
      <Products 
        category={category} 
        filters={filters}
        sort={sort}
      />
      <Newsletter />
      <Footer />
    </Container>
  );
};

export default ProductList;
