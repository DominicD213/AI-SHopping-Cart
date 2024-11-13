import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// API service for products
export const productService = {
  // Get all products
  async getProducts(filters = {}) {
    try {
      const response = await axios.post(`${API_URL}/search`, filters);
      return response.data.results;
    } catch (error) {
      console.error('Error fetching products:', error);
      return [];
    }
  },

  // Get product by ID
  async getProductById(id) {
    try {
      const response = await axios.get(`${API_URL}/products/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching product:', error);
      return null;
    }
  },

  // Get trending products
  async getTrendingProducts() {
    try {
      const response = await axios.get(`${API_URL}/trending`);
      return response.data.trending_products;
    } catch (error) {
      console.error('Error fetching trending products:', error);
      return [];
    }
  },

  // Get product recommendations
  async getRecommendations(productId) {
    try {
      const response = await axios.get(`${API_URL}/recommendations?product_id=${productId}`);
      return response.data.recommendations;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  }
};

// API service for cart
export const cartService = {
  // Get cart items
  async getCart() {
    try {
      const response = await axios.get(`${API_URL}/cart`);
      return response.data.cart_items;
    } catch (error) {
      console.error('Error fetching cart:', error);
      return [];
    }
  },

  // Add item to cart
  async addToCart(productId, quantity = 1) {
    try {
      const response = await axios.post(`${API_URL}/cart/add/${productId}`, { quantity });
      return response.data;
    } catch (error) {
      console.error('Error adding to cart:', error);
      throw error;
    }
  },

  // Remove item from cart
  async removeFromCart(productId) {
    try {
      const response = await axios.delete(`${API_URL}/cart/remove/${productId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing from cart:', error);
      throw error;
    }
  }
};

// API service for authentication
export const authService = {
  // Login
  async login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, { username, password });
      const { token } = response.data;
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = token;
      return response.data;
    } catch (error) {
      console.error('Error logging in:', error);
      throw error;
    }
  },

  // Register
  async register(username, email, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        username,
        email,
        password
      });
      return response.data;
    } catch (error) {
      console.error('Error registering:', error);
      throw error;
    }
  },

  // Logout
  logout() {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Setup axios interceptor for token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = token;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Categories based on our database schema
export const categories = [
  {
    id: 1,
    img: "https://images.pexels.com/photos/5886041/pexels-photo-5886041.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    title: "CLOTHING",
    category: "Clothing"
  },
  {
    id: 2,
    img: "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    title: "ELECTRONICS",
    category: "Electronics"
  },
  {
    id: 3,
    img: "https://images.pexels.com/photos/5480696/pexels-photo-5480696.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=500",
    title: "BOOKS",
    category: "Book"
  },
  {
    id: 4,
    img: "https://images.pexels.com/photos/2528118/pexels-photo-2528118.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    title: "MOVIES",
    category: "Movie"
  },
  {
    id: 5,
    img: "https://images.pexels.com/photos/1350789/pexels-photo-1350789.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    title: "FURNITURE",
    category: "Furniture"
  },
  {
    id: 6,
    img: "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    title: "FOOD",
    category: "Food"
  }
];

// Featured items for slider
export const sliderItems = [
  {
    id: 1,
    img: "https://www.coolfashiontrend.com/wp-content/uploads/2015/07/image-1.jpg",
    title: "NEW ARRIVALS",
    desc: "DISCOVER OUR LATEST COLLECTION OF PRODUCTS.",
    bg: "f5fafd",
  },
  {
    id: 2,
    img: "https://i.ibb.co/DG69bQ4/2.png",
    title: "TRENDING NOW",
    desc: "EXPLORE OUR MOST POPULAR ITEMS.",
    bg: "fcf1ed",
  },
  {
    id: 3,
    img: "https://assets.modelsdirect.com/blog/wp-content/uploads/2020/03/12152520/shutterstock_1114513799.jpg",
    title: "SPECIAL OFFERS",
    desc: "GREAT DEALS ON SELECTED ITEMS.",
    bg: "FDFFFF",
  },
];
